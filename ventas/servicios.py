from collections import defaultdict
from decimal import ROUND_UP, Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.formats import number_format

from caja.models import MovimientoCaja
from caja.servicios import caja_abierta, registrar_movimiento
from core.models import Configuracion
from inventario import servicios as inventario

from .models import DetalleVenta, EventoOrden, OrdenTrabajo, Pago, Venta


def _bs(monto):
    return f'Bs {number_format(monto, 2)}'


@transaction.atomic
def registrar_pago(venta, usuario, monto, forma_pago):
    """Cobra un pago de la venta y lo registra como ingreso en la caja abierta del usuario."""
    venta = Venta.objects.select_for_update().get(pk=venta.pk)
    if venta.estado != Venta.Estado.VIGENTE:
        raise ValidationError('No se puede cobrar una venta anulada.')
    if monto > venta.saldo:
        raise ValidationError(f'El pago supera el saldo pendiente ({_bs(venta.saldo)}).')
    movimiento = registrar_movimiento(
        usuario, MovimientoCaja.Tipo.INGRESO, forma_pago, monto, f'Pago de la nota de venta {venta.numero}',
    )
    return Pago.objects.create(
        venta=venta, usuario=usuario, movimiento_caja=movimiento, monto=monto, forma_pago=forma_pago,
    )


def _validar_lineas(lineas):
    if not lineas:
        raise ValidationError('Agregue al menos un artículo.')
    vistos = set()
    for articulo, cantidad in lineas:
        if articulo.pk in vistos:
            raise ValidationError(f'El artículo {articulo} está repetido. Sume las cantidades en una sola línea.')
        vistos.add(articulo.pk)
        if not articulo.activo:
            raise ValidationError(f'{articulo} está inactivo y no se puede vender.')
        if cantidad is None or cantidad < 1:
            raise ValidationError(f'La cantidad de {articulo} debe ser al menos 1.')


def anticipo_minimo(total):
    """Monto mínimo que debe pagarse al encargar lentes graduados (RF32), redondeado al centavo hacia arriba."""
    porcentaje = Configuracion.actual().anticipo_minimo_porcentaje
    return (total * porcentaje / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_UP)


@transaction.atomic
def registrar_venta(vendedor, lineas, monto_pago, forma_pago, cliente=None, cliente_nombre='', cliente_ci='',
                    descuento=Decimal('0'), observacion='', receta=None, fecha_prometida=None):
    """Registra la venta, descuenta el stock y cobra el pago inicial, todo en una transacción (RNF05).

    `lineas` = [(artículo, cantidad), ...]. El precio sale del catálogo; el vendedor solo puede aplicar
    un descuento global. Si falta stock de una línea o el pago no es válido, no se registra nada.

    Si se venden lentes graduados (artículos con `requiere_receta`), la venta exige un cliente registrado y una
    de sus recetas, un anticipo mínimo (RF32), y genera la orden de trabajo para el taller (RF23).
    Sin cliente registrado, basta con el nombre (cliente ocasional).
    """
    if caja_abierta(vendedor) is None:
        raise ValidationError('Debe abrir su caja antes de registrar ventas.')
    if vendedor.sucursal_id is None:
        raise ValidationError('No tiene una sucursal asignada. Pida al administrador que se la asigne.')
    _validar_lineas(lineas)
    if cliente:
        cliente_nombre, cliente_ci = cliente.nombre, cliente.ci_nit or ''
    elif not (cliente_nombre or '').strip():
        raise ValidationError('Elija un cliente registrado o escriba el nombre del cliente.')
    graduados = [a for a, _ in lineas if a.requiere_receta]
    if graduados:
        if not cliente:
            raise ValidationError('Los lentes graduados se venden a un cliente registrado: elíjalo o regístrelo.')
        if receta is None:
            raise ValidationError(f'Elija la receta de {cliente} para el taller.')
        if receta.cliente_id != cliente.pk:
            raise ValidationError(f'La receta elegida no es de {cliente}.')

    descuento = descuento or Decimal('0')
    subtotal = sum((a.precio_venta * c for a, c in lineas), Decimal('0'))
    if descuento < 0:
        raise ValidationError('El descuento no puede ser negativo.')
    if descuento >= subtotal:
        raise ValidationError(f'El descuento debe ser menor que el subtotal ({_bs(subtotal)}).')
    total = subtotal - descuento
    if monto_pago > total:
        raise ValidationError(f'El pago inicial no puede superar el total de la venta ({_bs(total)}).')
    if graduados and monto_pago < anticipo_minimo(total):
        porcentaje = Configuracion.actual().anticipo_minimo_porcentaje
        raise ValidationError(f'Los lentes graduados exigen un anticipo de al menos el {porcentaje} % '
                              f'del total: {_bs(anticipo_minimo(total))}.')

    venta = Venta.objects.create(
        vendedor=vendedor, sucursal_id=vendedor.sucursal_id, cliente=cliente, cliente_nombre=cliente_nombre.strip(),
        cliente_ci=(cliente_ci or '').strip(), descripcion=observacion.strip(), descuento=descuento, total=total,
    )
    if graduados:
        orden = OrdenTrabajo.objects.create(venta=venta, receta=receta, fecha_prometida=fecha_prometida)
        EventoOrden.objects.create(orden=orden, estado=orden.estado, usuario=vendedor,
                                   nota=f'Generada con la {venta}.')
    con_stock = [(a, c) for a, c in lineas if a.controla_stock]
    movimientos = inventario.registrar_salida_venta(
        vendedor, venta.sucursal, con_stock, str(venta)) if con_stock else {}
    DetalleVenta.objects.bulk_create([
        DetalleVenta(venta=venta, articulo=a, cantidad=c, precio_unitario=a.precio_venta,
                     costo_unitario=movimientos[a.pk].costo_unitario if a.pk in movimientos else a.costo_promedio)
        for a, c in lineas
    ])
    registrar_pago(venta, vendedor, monto_pago, forma_pago)
    return venta


@transaction.atomic
def anular_venta(venta, usuario, motivo):
    """Anula la venta: repone el stock y devuelve lo pagado desde la caja abierta de quien anula.

    La devolución se registra como egreso, uno por forma de pago, para que el arqueo la refleje.
    """
    motivo = (motivo or '').strip()
    if not motivo:
        raise ValidationError('Indique el motivo de la anulación.')
    venta = Venta.objects.select_for_update().get(pk=venta.pk)
    if venta.estado != Venta.Estado.VIGENTE:
        raise ValidationError(f'La {venta} ya está anulada.')
    orden = OrdenTrabajo.objects.select_for_update().filter(venta=venta).first()
    if orden and orden.estado == OrdenTrabajo.Estado.ENTREGADO:
        raise ValidationError(f'No se puede anular: el trabajo de la {orden} ya se entregó al cliente.')

    devoluciones = defaultdict(Decimal)
    for pago in venta.pagos.all():
        devoluciones[pago.forma_pago] += pago.monto
    if devoluciones and caja_abierta(usuario) is None:
        raise ValidationError(f'Abra su caja para devolver lo pagado ({_bs(venta.total_pagado)}) antes de anular.')
    for forma_pago, monto in sorted(devoluciones.items()):
        registrar_movimiento(usuario, MovimientoCaja.Tipo.EGRESO, forma_pago, monto,
                             f'Devolución por anulación de la nota de venta {venta.numero}')

    a_reponer = [(d.articulo, d.cantidad, d.costo_unitario)
                 for d in venta.detalles.select_related('articulo') if d.articulo.controla_stock]
    if a_reponer:
        inventario.reponer_venta(usuario, venta.sucursal, a_reponer, f'Anulación de la nota de venta {venta.numero}')

    venta.estado = Venta.Estado.ANULADA
    venta.usuario_anulacion = usuario
    venta.fecha_anulacion = timezone.now()
    venta.motivo_anulacion = motivo
    venta.save(update_fields=['estado', 'usuario_anulacion', 'fecha_anulacion', 'motivo_anulacion'])
    if orden:
        _cambiar_estado(orden, OrdenTrabajo.Estado.ANULADA, usuario, f'Venta anulada: {motivo}')
    return venta


# ---------- Órdenes de trabajo (RF24, RF31) ----------

def _cambiar_estado(orden, estado, usuario, nota=''):
    orden.estado = estado
    orden.save(update_fields=['estado'])
    EventoOrden.objects.create(orden=orden, estado=estado, usuario=usuario, nota=nota[:255])


def _bloquear(orden):
    return OrdenTrabajo.objects.select_for_update().select_related('venta').get(pk=orden.pk)


@transaction.atomic
def avanzar_orden(orden, usuario, nota=''):
    """El taller avanza la orden un paso: pendiente → en taller → listo."""
    orden = _bloquear(orden)
    siguiente = orden.siguiente_estado
    if siguiente is None:
        raise ValidationError(f'La {orden} está {orden.get_estado_display().lower()}: el taller ya no la modifica.')
    _cambiar_estado(orden, siguiente, usuario, (nota or '').strip())
    return orden


@transaction.atomic
def autorizar_entrega(orden, usuario, motivo):
    """El gerente autoriza entregar el trabajo aunque la venta tenga saldo pendiente. Queda registrado (RF31)."""
    motivo = (motivo or '').strip()
    if not motivo:
        raise ValidationError('Indique el motivo de la autorización.')
    orden = _bloquear(orden)
    if not orden.activa:
        raise ValidationError(f'La {orden} está {orden.get_estado_display().lower()}.')
    if orden.venta.saldo <= 0:
        raise ValidationError('La venta no tiene saldo pendiente: no hace falta autorizar la entrega.')
    if orden.entrega_autorizada:
        raise ValidationError('La entrega con saldo ya está autorizada.')
    orden.entrega_autorizada_por = usuario
    orden.fecha_autorizacion = timezone.now()
    orden.motivo_autorizacion = motivo
    orden.save(update_fields=['entrega_autorizada_por', 'fecha_autorizacion', 'motivo_autorizacion'])
    EventoOrden.objects.create(orden=orden, estado=orden.estado, usuario=usuario,
                               nota=f'Entrega con saldo de {_bs(orden.venta.saldo)} autorizada: {motivo}'[:255])
    return orden


@transaction.atomic
def entregar_orden(orden, usuario):
    """Entrega el trabajo al cliente. Con saldo pendiente, solo si el gerente lo autorizó (RF31)."""
    orden = _bloquear(orden)
    if orden.estado != OrdenTrabajo.Estado.LISTO:
        raise ValidationError(f'Solo se entrega un trabajo listo. La {orden} está '
                              f'{orden.get_estado_display().lower()}.')
    saldo = orden.venta.saldo
    if saldo > 0 and not orden.entrega_autorizada:
        raise ValidationError(f'La venta tiene un saldo pendiente de {_bs(saldo)}. Cóbrelo antes de entregar '
                              'o pida al gerente que autorice la entrega con saldo.')
    nota = f'Entregado con saldo pendiente de {_bs(saldo)}.' if saldo > 0 else 'Entregado con la venta pagada.'
    _cambiar_estado(orden, OrdenTrabajo.Estado.ENTREGADO, usuario, nota)
    return orden

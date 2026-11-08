from collections import defaultdict
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.formats import number_format

from caja.models import MovimientoCaja
from caja.servicios import caja_abierta, registrar_movimiento
from inventario import servicios as inventario

from .models import DetalleVenta, Pago, Venta


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


@transaction.atomic
def registrar_venta(vendedor, cliente_nombre, cliente_ci, lineas, monto_pago, forma_pago,
                    descuento=Decimal('0'), observacion=''):
    """Registra la venta, descuenta el stock y cobra el pago inicial, todo en una transacción (RNF05).

    `lineas` = [(artículo, cantidad), ...]. El precio sale del catálogo; el vendedor solo puede aplicar
    un descuento global. Si falta stock de una línea o el pago no es válido, no se registra nada.
    """
    if caja_abierta(vendedor) is None:
        raise ValidationError('Debe abrir su caja antes de registrar ventas.')
    if vendedor.sucursal_id is None:
        raise ValidationError('No tiene una sucursal asignada. Pida al administrador que se la asigne.')
    _validar_lineas(lineas)
    descuento = descuento or Decimal('0')
    subtotal = sum((a.precio_venta * c for a, c in lineas), Decimal('0'))
    if descuento < 0:
        raise ValidationError('El descuento no puede ser negativo.')
    if descuento >= subtotal:
        raise ValidationError(f'El descuento debe ser menor que el subtotal ({_bs(subtotal)}).')
    total = subtotal - descuento
    if monto_pago > total:
        raise ValidationError(f'El pago inicial no puede superar el total de la venta ({_bs(total)}).')

    venta = Venta.objects.create(
        vendedor=vendedor, sucursal_id=vendedor.sucursal_id, cliente_nombre=cliente_nombre,
        cliente_ci=cliente_ci, descripcion=observacion.strip(), descuento=descuento, total=total,
    )
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
    return venta

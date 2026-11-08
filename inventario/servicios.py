"""Operaciones que mueven stock (RNF05).

Cada función pública corre en una sola transacción: bloquea los artículos con
`select_for_update()` (en orden de pk, para evitar bloqueos mutuos), actualiza las
existencias y registra el kardex. Si una línea falla, no se aplica ninguna.
`ventas` reutiliza estas funciones; las vistas y el admin nunca tocan `Existencia`.
"""

from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import (
    ENTRADAS, Ajuste, Articulo, DetalleIngreso, DetalleTraspaso, Existencia, Ingreso, Movimiento, Traspaso,
)

CUATRO_DECIMALES = Decimal('0.0001')


# ---------- Utilidades internas ----------

def _bloquear_articulos(ids):
    """Bloquea los artículos hasta el final de la transacción y los devuelve por pk."""
    return {a.pk: a for a in Articulo.objects.select_for_update().filter(pk__in=ids).order_by('pk')}


def _validar_lineas(lineas, exigir_activos=False):
    """Revisa las líneas (artículo, cantidad, ...) antes de mover stock."""
    if not lineas:
        raise ValidationError('Agregue al menos un artículo.')
    vistos = set()
    for articulo, cantidad, *_ in lineas:
        if articulo.pk in vistos:
            raise ValidationError(f'El artículo {articulo} está repetido. Sume las cantidades en una sola línea.')
        vistos.add(articulo.pk)
        if not articulo.controla_stock:
            raise ValidationError(f'{articulo} es un servicio y no controla stock.')
        if exigir_activos and not articulo.activo:
            raise ValidationError(f'{articulo} está inactivo.')
        if cantidad is None or cantidad < 1:
            raise ValidationError(f'La cantidad de {articulo} debe ser al menos 1.')


def unidades_en_transito(articulo):
    """Unidades enviadas en traspasos que aún no se recibieron."""
    return DetalleTraspaso.objects.filter(
        articulo=articulo, traspaso__estado=Traspaso.Estado.ENVIADO,
    ).aggregate(total=Sum('cantidad'))['total'] or 0


def unidades_totales(articulo):
    """Todas las unidades de la empresa: existencias de todas las sucursales más las que están en tránsito."""
    en_sucursales = articulo.existencias.aggregate(total=Sum('cantidad'))['total'] or 0
    return en_sucursales + unidades_en_transito(articulo)


def costo_promedio_ponderado(unidades, costo_actual, cantidad, costo_compra):
    """(unidades × costo actual + cantidad × costo de compra) / (unidades + cantidad)."""
    total = unidades * costo_actual + cantidad * costo_compra
    return (total / (unidades + cantidad)).quantize(CUATRO_DECIMALES, rounding=ROUND_HALF_UP)


def _mover(articulo, sucursal, tipo, cantidad, costo_unitario, usuario, referencia, **documento):
    """Suma o resta stock en la sucursal y registra la línea del kardex.

    El artículo ya debe estar bloqueado por la transacción que llama.
    """
    existencia, _ = Existencia.objects.select_for_update().get_or_create(articulo=articulo, sucursal=sucursal)
    if tipo in ENTRADAS:
        existencia.cantidad += cantidad
    else:
        if existencia.cantidad < cantidad:
            raise ValidationError(
                f'Stock insuficiente de {articulo} en {sucursal}: hay {existencia.cantidad} '
                f'y se necesita{"n" if cantidad != 1 else ""} {cantidad}.')
        existencia.cantidad -= cantidad
    existencia.save(update_fields=['cantidad'])
    return Movimiento.objects.create(
        articulo=articulo, sucursal=sucursal, tipo=tipo, cantidad=cantidad, costo_unitario=costo_unitario,
        saldo=existencia.cantidad, costo_promedio=articulo.costo_promedio, usuario=usuario, referencia=referencia,
        **documento,
    )


def _validar_sucursal(sucursal, rol):
    if not sucursal.activa:
        raise ValidationError(f'La sucursal {rol} ({sucursal}) está inactiva.')


# ---------- Operaciones ----------

@transaction.atomic
def registrar_ingreso(usuario, sucursal, proveedor, lineas, documento='', observacion=''):
    """Ingreso por compra (RF09). `lineas` = [(artículo, cantidad, costo unitario), ...].

    Cada línea recalcula el costo promedio del artículo con el método de promedio ponderado.
    """
    _validar_sucursal(sucursal, 'de destino')
    if not proveedor.activo:
        raise ValidationError(f'El proveedor {proveedor} está inactivo.')
    _validar_lineas(lineas, exigir_activos=True)
    for articulo, _, costo in lineas:
        if costo is None or costo <= 0:
            raise ValidationError(f'El costo unitario de {articulo} debe ser mayor a cero.')

    ingreso = Ingreso.objects.create(usuario=usuario, sucursal=sucursal, proveedor=proveedor,
                                     documento=documento.strip(), observacion=observacion.strip())
    articulos = _bloquear_articulos([a.pk for a, *_ in lineas])
    for linea, cantidad, costo in sorted(lineas, key=lambda l: l[0].pk):
        articulo = articulos[linea.pk]
        DetalleIngreso.objects.create(ingreso=ingreso, articulo=articulo, cantidad=cantidad, costo_unitario=costo)
        articulo.costo_promedio = costo_promedio_ponderado(
            unidades_totales(articulo), articulo.costo_promedio, cantidad, costo)
        articulo.save(update_fields=['costo_promedio'])
        _mover(articulo, sucursal, Movimiento.Tipo.COMPRA, cantidad, costo, usuario, str(ingreso), ingreso=ingreso)
    return ingreso


@transaction.atomic
def registrar_ajuste(usuario, sucursal, articulo, tipo, cantidad, motivo):
    """Baja o ajuste por conteo físico, siempre con motivo. Se valora al costo promedio vigente."""
    motivo = (motivo or '').strip()
    if not motivo:
        raise ValidationError('Indique el motivo de la baja o del ajuste.')
    if tipo not in Ajuste.Tipo.values:
        raise ValidationError('Tipo de ajuste no válido.')
    _validar_sucursal(sucursal, 'del ajuste')
    _validar_lineas([(articulo, cantidad)])

    articulo = _bloquear_articulos([articulo.pk])[articulo.pk]
    ajuste = Ajuste.objects.create(usuario=usuario, sucursal=sucursal, articulo=articulo, tipo=tipo,
                                   cantidad=cantidad, motivo=motivo)
    _mover(articulo, sucursal, Movimiento.Tipo(tipo), cantidad, articulo.costo_promedio, usuario, str(ajuste),
           ajuste=ajuste)
    return ajuste


@transaction.atomic
def enviar_traspaso(usuario, origen, destino, lineas, observacion=''):
    """Primer paso del traspaso: la mercadería sale del stock del origen. `lineas` = [(artículo, cantidad), ...]."""
    if origen.pk == destino.pk:
        raise ValidationError('La sucursal de destino debe ser distinta de la de origen.')
    _validar_sucursal(origen, 'de origen')
    _validar_sucursal(destino, 'de destino')
    _validar_lineas(lineas)

    traspaso = Traspaso.objects.create(origen=origen, destino=destino, usuario_envio=usuario,
                                       observacion=observacion.strip())
    articulos = _bloquear_articulos([a.pk for a, _ in lineas])
    for linea, cantidad in sorted(lineas, key=lambda l: l[0].pk):
        articulo = articulos[linea.pk]
        DetalleTraspaso.objects.create(traspaso=traspaso, articulo=articulo, cantidad=cantidad)
        _mover(articulo, origen, Movimiento.Tipo.TRASPASO_SALIDA, cantidad, articulo.costo_promedio, usuario,
               str(traspaso), traspaso=traspaso)
    return traspaso


@transaction.atomic
def registrar_salida_venta(usuario, sucursal, lineas, referencia):
    """Descuenta del stock de la sucursal los artículos vendidos (RF10, RNF05).

    `lineas` = [(artículo, cantidad), ...], solo artículos que controlan stock. Se valoran al costo
    promedio vigente. Devuelve {pk del artículo: movimiento} para que la venta guarde el costo.
    `ventas` llama a esta función dentro de la misma transacción en la que crea la venta.
    """
    _validar_sucursal(sucursal, 'de la venta')
    _validar_lineas(lineas, exigir_activos=True)
    articulos = _bloquear_articulos([a.pk for a, _ in lineas])
    movimientos = {}
    for linea, cantidad in sorted(lineas, key=lambda l: l[0].pk):
        articulo = articulos[linea.pk]
        movimientos[articulo.pk] = _mover(articulo, sucursal, Movimiento.Tipo.VENTA, cantidad,
                                          articulo.costo_promedio, usuario, referencia)
    return movimientos


@transaction.atomic
def reponer_venta(usuario, sucursal, lineas, referencia):
    """Devuelve al stock lo vendido cuando se anula la venta. `lineas` = [(artículo, cantidad, costo), ...].

    Las unidades vuelven al costo con el que salieron, así que el costo promedio se recalcula como en una compra.
    """
    _validar_lineas(lineas)
    articulos = _bloquear_articulos([a.pk for a, *_ in lineas])
    for linea, cantidad, costo in sorted(lineas, key=lambda l: l[0].pk):
        articulo = articulos[linea.pk]
        articulo.costo_promedio = costo_promedio_ponderado(
            unidades_totales(articulo), articulo.costo_promedio, cantidad, costo)
        articulo.save(update_fields=['costo_promedio'])
        _mover(articulo, sucursal, Movimiento.Tipo.ANULACION_VENTA, cantidad, costo, usuario, referencia)


@transaction.atomic
def recibir_traspaso(traspaso, usuario):
    """Segundo paso: quien está en la sucursal de destino confirma la recepción y la mercadería entra a su stock."""
    traspaso = Traspaso.objects.select_for_update().get(pk=traspaso.pk)
    if traspaso.estado != Traspaso.Estado.ENVIADO:
        raise ValidationError(f'El {traspaso} ya fue recibido.')
    if usuario.sucursal_id != traspaso.destino_id:
        raise ValidationError(f'Solo el personal de {traspaso.destino} puede recibir este traspaso.')

    detalles = list(traspaso.detalles.order_by('articulo_id'))
    articulos = _bloquear_articulos([d.articulo_id for d in detalles])
    for detalle in detalles:
        articulo = articulos[detalle.articulo_id]
        _mover(articulo, traspaso.destino, Movimiento.Tipo.TRASPASO_ENTRADA, detalle.cantidad,
               articulo.costo_promedio, usuario, str(traspaso), traspaso=traspaso)
    traspaso.estado = Traspaso.Estado.RECIBIDO
    traspaso.usuario_recepcion = usuario
    traspaso.fecha_recepcion = timezone.now()
    traspaso.save(update_fields=['estado', 'usuario_recepcion', 'fecha_recepcion'])
    return traspaso

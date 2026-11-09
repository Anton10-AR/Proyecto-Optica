"""Reportes de ventas por período, vendedor y producto (RF07). Consultas de solo lectura.

Cuentan las ventas vigentes registradas en el período; las anuladas se informan aparte. Los cobros son los pagos
recibidos en el período, sin los de ventas anuladas (que se devolvieron). El importe por producto es a precio de
lista: el descuento es global a la venta y no se reparte entre las líneas.
"""

from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone

from caja.models import FormaPago

from .models import DetalleVenta, Pago, Venta

CERO = Decimal('0')
DINERO = DecimalField(max_digits=14, decimal_places=4)


def _rango(desde, hasta):
    """Límites con zona horaria para filtrar fechas y horas de un período de días completos."""
    return (timezone.make_aware(datetime.combine(desde, time.min)),
            timezone.make_aware(datetime.combine(hasta + timedelta(days=1), time.min)))


def _ventas(desde, hasta, sucursal=None, vendedor=None):
    inicio, fin = _rango(desde, hasta)
    ventas = Venta.objects.filter(fecha__gte=inicio, fecha__lt=fin)
    if sucursal:
        ventas = ventas.filter(sucursal=sucursal)
    if vendedor:
        ventas = ventas.filter(vendedor=vendedor)
    return ventas


def _suma(campo):
    return Coalesce(Sum(campo), CERO, output_field=DecimalField(max_digits=14, decimal_places=2))


def resumen(desde, hasta, sucursal=None, vendedor=None):
    ventas = _ventas(desde, hasta, sucursal, vendedor)
    vigentes = ventas.filter(estado=Venta.Estado.VIGENTE)
    totales = vigentes.aggregate(cantidad=Count('id'), total=_suma('total'), descuentos=_suma('descuento'))
    totales['ticket_promedio'] = (totales['total'] / totales['cantidad']).quantize(Decimal('0.01')) if totales['cantidad'] else CERO
    totales['saldo'] = sum((v.saldo for v in vigentes.prefetch_related('pagos')), CERO)
    totales['anuladas'] = ventas.filter(estado=Venta.Estado.ANULADA).aggregate(cantidad=Count('id'), total=_suma('total'))

    inicio, fin = _rango(desde, hasta)
    pagos = Pago.objects.filter(fecha__gte=inicio, fecha__lt=fin, venta__estado=Venta.Estado.VIGENTE)
    if sucursal:
        pagos = pagos.filter(venta__sucursal=sucursal)
    if vendedor:
        pagos = pagos.filter(venta__vendedor=vendedor)
    por_forma = dict(pagos.values_list('forma_pago').annotate(total=_suma('monto')))
    totales['cobros'] = [(etiqueta, por_forma.get(valor, CERO)) for valor, etiqueta in FormaPago.choices]
    totales['cobrado'] = sum(por_forma.values(), CERO)

    dias = (vigentes.annotate(dia=TruncDate('fecha', tzinfo=timezone.get_current_timezone()))
            .values('dia').annotate(cantidad=Count('id'), total=_suma('total')).order_by('dia'))
    totales['dias'] = list(dias)
    maximo = max((d['total'] for d in totales['dias']), default=CERO)
    for d in totales['dias']:
        d['porcentaje'] = int(d['total'] * 100 / maximo) if maximo else 0
    return totales


def por_vendedor(desde, hasta, sucursal=None, vendedor=None):
    filas = {}
    for v in (_ventas(desde, hasta, sucursal, vendedor).filter(estado=Venta.Estado.VIGENTE)
              .select_related('vendedor', 'sucursal').prefetch_related('pagos')):
        fila = filas.setdefault(v.vendedor_id, {'vendedor': v.vendedor, 'sucursales': set(), 'cantidad': 0,
                                                'total': CERO, 'descuentos': CERO, 'saldo': CERO})
        fila['sucursales'].add(v.sucursal.nombre)
        fila['cantidad'] += 1
        fila['total'] += v.total
        fila['descuentos'] += v.descuento
        fila['saldo'] += v.saldo
    for fila in filas.values():
        fila['ticket_promedio'] = (fila['total'] / fila['cantidad']).quantize(Decimal('0.01'))
        fila['sucursales'] = ', '.join(sorted(fila['sucursales']))
    return sorted(filas.values(), key=lambda f: f['total'], reverse=True)


def por_producto(desde, hasta, sucursal=None, vendedor=None):
    """Unidades, importe a precio de lista, costo y margen de cada artículo vendido."""
    ventas = _ventas(desde, hasta, sucursal, vendedor).filter(estado=Venta.Estado.VIGENTE)
    filas = list(
        DetalleVenta.objects.filter(venta__in=ventas)
        .values('articulo_id', 'articulo__codigo', 'articulo__nombre', 'articulo__categoria__nombre',
                'articulo__controla_stock')
        .annotate(unidades=Sum('cantidad'),
                  importe=Sum(ExpressionWrapper(F('cantidad') * F('precio_unitario'), output_field=DINERO)),
                  costo=Sum(ExpressionWrapper(F('cantidad') * F('costo_unitario'), output_field=DINERO)))
        .order_by('-importe'))
    for f in filas:
        f['importe'] = f['importe'].quantize(Decimal('0.01'))
        f['costo'] = f['costo'].quantize(Decimal('0.01'))
        f['margen'] = f['importe'] - f['costo']
        f['margen_porcentaje'] = (f['margen'] * 100 / f['importe']).quantize(Decimal('0.1')) if f['importe'] else None
    sin_detalle = ventas.filter(detalles__isnull=True).count()
    return filas, sin_detalle

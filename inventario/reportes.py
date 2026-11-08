"""Consultas de solo lectura: alertas de stock mínimo (RF12) y reportes de existencias e inventario valorado (RF14).

Las usan las vistas de inventario y el panel de inicio. No modifican nada.
"""

from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum

from core.models import Sucursal

from .models import Articulo, DetalleTraspaso, Existencia, Traspaso


def _cantidades(articulos, sucursales):
    """{(pk del artículo, pk de la sucursal): unidades}. Sin fila de existencia, el stock es 0."""
    filas = Existencia.objects.filter(articulo__in=articulos, sucursal__in=sucursales)
    return {(a, s): c for a, s, c in filas.values_list('articulo_id', 'sucursal_id', 'cantidad')}


def _en_transito(articulos):
    """{pk del artículo: unidades enviadas en traspasos que aún no se recibieron}."""
    filas = DetalleTraspaso.objects.filter(articulo__in=articulos, traspaso__estado=Traspaso.Estado.ENVIADO)
    return dict(filas.values('articulo_id').annotate(total=Sum('cantidad')).values_list('articulo_id', 'total'))


def articulos_con_stock(categoria=None):
    articulos = Articulo.objects.filter(activo=True, controla_stock=True).select_related('categoria')
    if categoria:
        articulos = articulos.filter(categoria=categoria)
    return articulos.order_by('categoria__nombre', 'nombre')


def alertas_stock(sucursales=None):
    """Artículos que llegaron a su stock mínimo en una sucursal (cantidad <= mínimo).

    Solo cuentan los artículos activos que controlan stock y tienen un mínimo mayor que cero, en sucursales
    activas. Cada alerta indica cuánto hay en las demás sucursales, para decidir entre comprar o traspasar.
    """
    todas = list(Sucursal.objects.filter(activa=True))
    elegidas = [s for s in todas if sucursales is None or s in sucursales]
    articulos = list(Articulo.objects.filter(activo=True, controla_stock=True, stock_minimo__gt=0)
                     .select_related('categoria').order_by('nombre'))
    cantidades = _cantidades(articulos, todas)
    alertas = []
    for sucursal in elegidas:
        for articulo in articulos:
            cantidad = cantidades.get((articulo.pk, sucursal.pk), 0)
            if cantidad <= articulo.stock_minimo:
                otras = [(s, cantidades.get((articulo.pk, s.pk), 0)) for s in todas if s != sucursal]
                alertas.append({
                    'articulo': articulo, 'sucursal': sucursal, 'cantidad': cantidad,
                    'agotado': cantidad == 0, 'otras': [(s, c) for s, c in otras if c > 0],
                })
    # Primero los agotados, luego los que tienen menos stock en relación con su mínimo.
    alertas.sort(key=lambda a: (a['sucursal'].nombre, a['cantidad'] > 0, a['cantidad'] / a['articulo'].stock_minimo,
                                a['articulo'].nombre))
    return alertas


def reporte_existencias(categoria=None):
    """Unidades de cada artículo en cada sucursal activa, más las que están en tránsito."""
    sucursales = list(Sucursal.objects.filter(activa=True))
    articulos = list(articulos_con_stock(categoria))
    cantidades = _cantidades(articulos, sucursales)
    transito = _en_transito(articulos)
    filas, totales = [], defaultdict(int)
    for articulo in articulos:
        celdas = []
        for s in sucursales:
            cantidad = cantidades.get((articulo.pk, s.pk), 0)
            celdas.append({'cantidad': cantidad, 'bajo_minimo': articulo.stock_minimo > 0
                           and cantidad <= articulo.stock_minimo})
            totales[s.pk] += cantidad
        en_transito = transito.get(articulo.pk, 0)
        total = sum(c['cantidad'] for c in celdas) + en_transito
        totales['transito'] += en_transito
        totales['total'] += total
        filas.append({'articulo': articulo, 'celdas': celdas, 'en_transito': en_transito, 'total': total})
    return {'sucursales': sucursales, 'filas': filas,
            'totales': [totales[s.pk] for s in sucursales], 'total_transito': totales['transito'],
            'total': totales['total']}


def reporte_valorado(sucursal=None, categoria=None):
    """Inventario valorado al costo promedio: de una sucursal o consolidado de toda la empresa.

    El consolidado incluye las unidades en tránsito, porque siguen siendo de la empresa.
    """
    sucursales = [sucursal] if sucursal else list(Sucursal.objects.filter(activa=True))
    articulos = list(articulos_con_stock(categoria))
    cantidades = _cantidades(articulos, sucursales)
    transito = {} if sucursal else _en_transito(articulos)
    grupos, total_unidades, total_valor = {}, 0, Decimal('0')
    for articulo in articulos:
        unidades = sum(cantidades.get((articulo.pk, s.pk), 0) for s in sucursales) + transito.get(articulo.pk, 0)
        if not unidades:
            continue
        valor = (unidades * articulo.costo_promedio).quantize(Decimal('0.01'))
        grupo = grupos.setdefault(articulo.categoria_id, {
            'categoria': articulo.categoria, 'filas': [], 'unidades': 0, 'valor': Decimal('0')})
        grupo['filas'].append({'articulo': articulo, 'unidades': unidades, 'en_transito': transito.get(articulo.pk, 0),
                               'costo': articulo.costo_promedio, 'valor': valor})
        grupo['unidades'] += unidades
        grupo['valor'] += valor
        total_unidades += unidades
        total_valor += valor
    return {'grupos': list(grupos.values()), 'unidades': total_unidades, 'valor': total_valor,
            'incluye_transito': not sucursal}


def ve_todas_las_sucursales(usuario):
    """Quien controla el inventario de la empresa ve las alertas de todas las sucursales; el resto, las de la suya."""
    return usuario.has_perm('inventario.ver_kardex') or usuario.has_perm('inventario.enviar_traspasos')

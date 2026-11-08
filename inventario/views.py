import csv
from decimal import Decimal
from functools import wraps
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from core.models import Sucursal
from core.views import PermisoMixin

from . import reportes, servicios
from .forms import (
    AjusteForm, ArticuloForm, CategoriaForm, IngresoForm, LineasIngresoFormSet, LineasTraspasoFormSet, ProveedorForm,
    TraspasoForm,
)
from .models import Ajuste, Articulo, Categoria, Ingreso, Proveedor, Traspaso


class MensajeGuardadoMixin:
    """Muestra un mensaje de éxito al crear o editar."""

    mensaje = 'Se guardó {objeto}.'

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, self.mensaje.format(objeto=self.object))
        return respuesta


def requiere_alguno(*permisos):
    """Como permission_required, pero basta con tener uno de los permisos."""
    def decorador(vista):
        @login_required
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not any(request.user.has_perm(p) for p in permisos):
                raise PermissionDenied
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


def _con_servicio(form, operacion):
    """Ejecuta la operación del servicio; si la rechaza, muestra el motivo en el formulario."""
    try:
        return operacion()
    except ValidationError as error:
        for mensaje in error.messages:
            form.add_error(None, mensaje)
        return None


# ---------- Artículos ----------

@login_required
@permission_required('inventario.ver_articulos', raise_exception=True)
def articulo_lista(request):
    articulos = Articulo.objects.select_related('categoria').annotate(
        stock_total=Coalesce(Sum('existencias__cantidad'), 0)).order_by('nombre')
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    estado = request.GET.get('estado', 'activo')
    if q:
        # Un lector de código de barras funciona como teclado: escribe el código en este campo.
        articulos = articulos.filter(
            Q(codigo__icontains=q) | Q(codigo_barras=q) | Q(nombre__icontains=q) | Q(marca__icontains=q))
    if categoria:
        articulos = articulos.filter(categoria_id=categoria)
    if estado in ('activo', 'inactivo'):
        articulos = articulos.filter(activo=(estado == 'activo'))
    pagina = Paginator(articulos, 20).get_page(request.GET.get('pagina'))
    contexto = {'pagina': pagina, 'categorias': Categoria.objects.all(),
                'q': q, 'categoria': categoria, 'estado': estado,
                'filtros': urlencode({'q': q, 'categoria': categoria, 'estado': estado})}
    plantilla = 'inventario/articulos/_tabla.html' if request.headers.get('HX-Request') else 'inventario/articulos/lista.html'
    return render(request, plantilla, contexto)


@login_required
@permission_required('inventario.ver_articulos', raise_exception=True)
def articulo_detalle(request, pk):
    articulo = get_object_or_404(Articulo.objects.select_related('categoria', 'proveedor'), pk=pk)
    cantidades = dict(articulo.existencias.values_list('sucursal_id', 'cantidad'))
    # Se listan todas las sucursales activas, también las que aún no tienen existencias del artículo.
    existencias = [(s, cantidades.get(s.pk, 0)) for s in Sucursal.objects.filter(activa=True)]
    contexto = {'articulo': articulo, 'existencias': existencias,
                'stock_total': sum(cantidades.values()),
                'en_transito': servicios.unidades_en_transito(articulo)}
    return render(request, 'inventario/articulos/detalle.html', contexto)


class ArticuloFormMixin(PermisoMixin, MensajeGuardadoMixin):
    permission_required = 'inventario.gestionar_catalogo'
    model = Articulo
    form_class = ArticuloForm
    template_name = 'inventario/articulos/form.html'

    def get_success_url(self):
        return reverse_lazy('articulo_detalle', args=[self.object.pk])


class ArticuloCrearView(ArticuloFormMixin, CreateView):
    mensaje = 'Se registró el artículo {objeto}.'


class ArticuloEditarView(ArticuloFormMixin, UpdateView):
    mensaje = 'Se actualizó el artículo {objeto}.'


# ---------- Categorías ----------

class CategoriaListaView(PermisoMixin, ListView):
    permission_required = 'inventario.gestionar_catalogo'
    template_name = 'inventario/categorias/lista.html'

    def get_queryset(self):
        return Categoria.objects.annotate(cantidad=Count('articulos')).order_by('nombre')


class CategoriaFormMixin(PermisoMixin, MensajeGuardadoMixin):
    permission_required = 'inventario.gestionar_catalogo'
    model = Categoria
    form_class = CategoriaForm
    template_name = 'inventario/categorias/form.html'
    success_url = reverse_lazy('categoria_lista')
    mensaje = 'Se guardó la categoría {objeto}.'


class CategoriaCrearView(CategoriaFormMixin, CreateView):
    pass


class CategoriaEditarView(CategoriaFormMixin, UpdateView):
    pass


# ---------- Proveedores ----------

@login_required
@permission_required('inventario.gestionar_proveedores', raise_exception=True)
def proveedor_lista(request):
    proveedores = Proveedor.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        proveedores = proveedores.filter(
            Q(razon_social__icontains=q) | Q(nit__icontains=q) | Q(contacto__icontains=q))
    pagina = Paginator(proveedores, 20).get_page(request.GET.get('pagina'))
    contexto = {'pagina': pagina, 'q': q, 'filtros': urlencode({'q': q})}
    plantilla = 'inventario/proveedores/_tabla.html' if request.headers.get('HX-Request') else 'inventario/proveedores/lista.html'
    return render(request, plantilla, contexto)


class ProveedorFormMixin(PermisoMixin, MensajeGuardadoMixin):
    permission_required = 'inventario.gestionar_proveedores'
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'inventario/proveedores/form.html'
    success_url = reverse_lazy('proveedor_lista')
    mensaje = 'Se guardó el proveedor {objeto}.'


class ProveedorCrearView(ProveedorFormMixin, CreateView):
    pass


class ProveedorEditarView(ProveedorFormMixin, UpdateView):
    pass


# ---------- Ingresos por compra ----------

@requiere_alguno('inventario.registrar_ingresos', 'inventario.ver_kardex')
def ingreso_lista(request):
    ingresos = Ingreso.objects.select_related('sucursal', 'proveedor', 'usuario').prefetch_related('detalles')
    pagina = Paginator(ingresos, 20).get_page(request.GET.get('pagina'))
    return render(request, 'inventario/ingresos/lista.html', {'pagina': pagina, 'filtros': ''})


@login_required
@permission_required('inventario.registrar_ingresos', raise_exception=True)
def ingreso_crear(request):
    form = IngresoForm(request.POST or None, usuario=request.user)
    lineas = LineasIngresoFormSet(request.POST or None, prefix='lineas')
    if request.method == 'POST' and form.is_valid() and lineas.is_valid():
        d = form.cleaned_data
        ingreso = _con_servicio(form, lambda: servicios.registrar_ingreso(
            request.user, d['sucursal'], d['proveedor'], lineas.lineas('cantidad', 'costo_unitario'),
            d['documento'], d['observacion']))
        if ingreso:
            messages.success(request, f'Se registró el {ingreso}: el stock y el costo promedio se actualizaron.')
            return redirect('ingreso_detalle', ingreso.pk)
    return render(request, 'inventario/ingresos/form.html', {'form': form, 'lineas': lineas})


@requiere_alguno('inventario.registrar_ingresos', 'inventario.ver_kardex')
def ingreso_detalle(request, pk):
    ingreso = get_object_or_404(Ingreso.objects.select_related('sucursal', 'proveedor', 'usuario'), pk=pk)
    detalles = ingreso.detalles.select_related('articulo')
    return render(request, 'inventario/ingresos/detalle.html', {'ingreso': ingreso, 'detalles': detalles})


# ---------- Bajas y ajustes ----------

@requiere_alguno('inventario.registrar_ajustes', 'inventario.ver_kardex')
def ajuste_lista(request):
    ajustes = Ajuste.objects.select_related('sucursal', 'articulo', 'usuario')
    pagina = Paginator(ajustes, 20).get_page(request.GET.get('pagina'))
    return render(request, 'inventario/ajustes/lista.html', {'pagina': pagina, 'filtros': ''})


@login_required
@permission_required('inventario.registrar_ajustes', raise_exception=True)
def ajuste_crear(request):
    form = AjusteForm(request.POST or None, usuario=request.user, initial={'articulo': request.GET.get('articulo')})
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        ajuste = _con_servicio(form, lambda: servicios.registrar_ajuste(
            request.user, d['sucursal'], d['articulo'], d['tipo'], d['cantidad'], d['motivo']))
        if ajuste:
            messages.success(request, f'Se registró: {ajuste.get_tipo_display().lower()} de {ajuste.cantidad} '
                                      f'× {ajuste.articulo} en {ajuste.sucursal}.')
            return redirect('ajuste_lista')
    return render(request, 'inventario/ajustes/form.html', {'form': form})


# ---------- Traspasos ----------

@requiere_alguno('inventario.enviar_traspasos', 'inventario.recibir_traspasos', 'inventario.ver_kardex')
def traspaso_lista(request):
    traspasos = Traspaso.objects.select_related('origen', 'destino', 'usuario_envio', 'usuario_recepcion')
    estado = request.GET.get('estado', '')
    if estado in Traspaso.Estado.values:
        traspasos = traspasos.filter(estado=estado)
    pagina = Paginator(traspasos, 20).get_page(request.GET.get('pagina'))
    por_recibir = Traspaso.objects.filter(estado=Traspaso.Estado.ENVIADO, destino_id=request.user.sucursal_id).count()
    contexto = {'pagina': pagina, 'estado': estado, 'estados': Traspaso.Estado.choices,
                'por_recibir': por_recibir, 'filtros': urlencode({'estado': estado})}
    return render(request, 'inventario/traspasos/lista.html', contexto)


@login_required
@permission_required('inventario.enviar_traspasos', raise_exception=True)
def traspaso_crear(request):
    form = TraspasoForm(request.POST or None, usuario=request.user)
    lineas = LineasTraspasoFormSet(request.POST or None, prefix='lineas')
    if request.method == 'POST' and form.is_valid() and lineas.is_valid():
        d = form.cleaned_data
        traspaso = _con_servicio(form, lambda: servicios.enviar_traspaso(
            request.user, d['origen'], d['destino'], lineas.lineas('cantidad'), d['observacion']))
        if traspaso:
            messages.success(request, f'Se envió el {traspaso} a {traspaso.destino}. '
                                      'La mercadería entrará a su stock cuando la reciban.')
            return redirect('traspaso_detalle', traspaso.pk)
    return render(request, 'inventario/traspasos/form.html', {'form': form, 'lineas': lineas})


@requiere_alguno('inventario.enviar_traspasos', 'inventario.recibir_traspasos', 'inventario.ver_kardex')
def traspaso_detalle(request, pk):
    traspaso = get_object_or_404(
        Traspaso.objects.select_related('origen', 'destino', 'usuario_envio', 'usuario_recepcion'), pk=pk)
    puede_recibir = (traspaso.estado == Traspaso.Estado.ENVIADO
                     and request.user.has_perm('inventario.recibir_traspasos')
                     and request.user.sucursal_id == traspaso.destino_id)
    contexto = {'traspaso': traspaso, 'detalles': traspaso.detalles.select_related('articulo'),
                'puede_recibir': puede_recibir}
    return render(request, 'inventario/traspasos/detalle.html', contexto)


@require_POST
@login_required
@permission_required('inventario.recibir_traspasos', raise_exception=True)
def traspaso_recibir(request, pk):
    traspaso = get_object_or_404(Traspaso, pk=pk)
    try:
        servicios.recibir_traspaso(traspaso, request.user)
        messages.success(request, f'Se recibió el {traspaso}: la mercadería ya está en el stock de {traspaso.destino}.')
    except ValidationError as error:
        messages.error(request, ' '.join(error.messages))
    return redirect('traspaso_detalle', traspaso.pk)


# ---------- Kardex ----------

@login_required
@permission_required('inventario.ver_kardex', raise_exception=True)
def kardex(request, pk):
    articulo = get_object_or_404(Articulo, pk=pk)
    sucursales = Sucursal.objects.filter(activa=True)
    elegida = request.GET.get('sucursal') or request.user.sucursal_id
    sucursal = (sucursales.filter(pk=elegida).first() if str(elegida or '').isdigit() else None) or sucursales.first()
    movimientos = articulo.movimientos.filter(sucursal=sucursal).select_related('usuario')
    contexto = {'articulo': articulo, 'sucursal': sucursal, 'sucursales': sucursales,
                'pagina': Paginator(movimientos, 50).get_page(request.GET.get('pagina')),
                'filtros': urlencode({'sucursal': sucursal.pk if sucursal else ''}),
                'en_transito': servicios.unidades_en_transito(articulo)}
    return render(request, 'inventario/kardex.html', contexto)


# ---------- Alertas y reportes ----------

def _sucursal_elegida(request, por_defecto=None):
    """Sucursal activa del parámetro ?sucursal=; con "todas" o sin parámetro válido, la de por defecto."""
    valor = request.GET.get('sucursal')
    if valor is None:
        return por_defecto
    return Sucursal.objects.filter(activa=True, pk=valor).first() if valor.isdigit() else None


def _categoria_elegida(request):
    valor = request.GET.get('categoria', '')
    return Categoria.objects.filter(pk=valor).first() if valor.isdigit() else None


def _numero(valor):
    """Número con coma decimal, como lo espera Excel en español."""
    return str(valor).replace('.', ',')


def _csv(nombre, encabezados, filas):
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre}.csv"'
    respuesta.write('﻿')  # BOM: Excel abre el archivo como UTF-8 y muestra bien las tildes.
    escritor = csv.writer(respuesta, delimiter=';')
    escritor.writerow(encabezados)
    escritor.writerows(filas)
    return respuesta


@login_required
@permission_required('inventario.ver_articulos', raise_exception=True)
def alertas_stock(request):
    """Artículos que llegaron a su stock mínimo (RF12)."""
    propia = None if reportes.ve_todas_las_sucursales(request.user) else request.user.sucursal
    sucursal = _sucursal_elegida(request, por_defecto=propia)
    alertas = reportes.alertas_stock([sucursal] if sucursal else None)
    return render(request, 'inventario/reportes/alertas.html', {
        'alertas': alertas, 'sucursal': sucursal, 'sucursales': Sucursal.objects.filter(activa=True),
        'agotados': sum(1 for a in alertas if a['agotado']),
    })


@login_required
@permission_required('inventario.ver_articulos', raise_exception=True)
def reporte_existencias(request):
    """Existencias por sucursal y consolidadas (RF14)."""
    categoria = _categoria_elegida(request)
    datos = reportes.reporte_existencias(categoria)
    if request.GET.get('formato') == 'csv':
        encabezados = ['Código', 'Artículo', 'Categoría', 'Stock mínimo'] + [s.nombre for s in datos['sucursales']]             + ['En tránsito', 'Total']
        filas = [[f['articulo'].codigo, f['articulo'].nombre, f['articulo'].categoria.nombre, f['articulo'].stock_minimo]
                 + [c['cantidad'] for c in f['celdas']] + [f['en_transito'], f['total']] for f in datos['filas']]
        filas.append(['', 'Total', '', ''] + datos['totales'] + [datos['total_transito'], datos['total']])
        return _csv(f'existencias_{timezone.localdate():%Y-%m-%d}', encabezados, filas)
    return render(request, 'inventario/reportes/existencias.html', {
        **datos, 'categoria': categoria, 'categorias': Categoria.objects.order_by('nombre'), 'hoy': timezone.localtime(),
        'filtros': urlencode({'categoria': categoria.pk if categoria else ''}),
    })


@login_required
@permission_required('inventario.ver_kardex', raise_exception=True)
def reporte_valorado(request):
    """Inventario valorado al costo promedio, por sucursal o consolidado (RF14)."""
    sucursal = _sucursal_elegida(request)
    categoria = _categoria_elegida(request)
    datos = reportes.reporte_valorado(sucursal, categoria)
    if request.GET.get('formato') == 'csv':
        filas = [[f['articulo'].codigo, f['articulo'].nombre, g['categoria'].nombre, f['unidades'],
                  _numero(f['costo'].quantize(Decimal('0.01'))), _numero(f['valor'])]
                 for g in datos['grupos'] for f in g['filas']]
        filas.append(['', 'Total', '', datos['unidades'], '', _numero(datos['valor'])])
        alcance = sucursal.nombre if sucursal else 'consolidado'
        return _csv(f'inventario_valorado_{alcance}_{timezone.localdate():%Y-%m-%d}'.replace(' ', '_'),
                    ['Código', 'Artículo', 'Categoría', 'Unidades', 'Costo promedio (Bs)', 'Valor (Bs)'], filas)
    return render(request, 'inventario/reportes/valorado.html', {
        **datos, 'sucursal': sucursal, 'categoria': categoria, 'hoy': timezone.localtime(),
        'sucursales': Sucursal.objects.filter(activa=True), 'categorias': Categoria.objects.order_by('nombre'),
        'filtros': urlencode({'sucursal': sucursal.pk if sucursal else '', 'categoria': categoria.pk if categoria else ''}),
    })

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from core.models import Sucursal
from core.views import PermisoMixin

from .forms import ArticuloForm, CategoriaForm, ProveedorForm
from .models import Articulo, Categoria, Proveedor


class MensajeGuardadoMixin:
    """Muestra un mensaje de éxito al crear o editar."""

    mensaje = 'Se guardó {objeto}.'

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, self.mensaje.format(objeto=self.object))
        return respuesta


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
                'stock_total': sum(cantidades.values())}
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

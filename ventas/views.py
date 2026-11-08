from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from caja.servicios import caja_abierta

from . import servicios
from .forms import AnularForm, LineasVentaFormSet, PagoForm, VentaForm
from .models import Venta


def _puede_ver_venta(usuario, venta):
    return venta.vendedor == usuario or usuario.has_perm('ventas.ver_todas_ventas')


@login_required
def lista(request):
    usuario = request.user
    if usuario.has_perm('ventas.ver_todas_ventas'):
        ventas = Venta.objects.all()
    elif usuario.has_perm('ventas.registrar_venta'):
        ventas = Venta.objects.filter(vendedor=usuario)
    else:
        raise PermissionDenied
    ventas = ventas.select_related('vendedor', 'sucursal')
    pagina = Paginator(ventas, 20).get_page(request.GET.get('pagina'))
    return render(request, 'ventas/lista.html', {'pagina': pagina})


@login_required
@permission_required('ventas.registrar_venta', raise_exception=True)
def crear(request):
    if caja_abierta(request.user) is None:
        messages.warning(request, 'Debe abrir su caja antes de registrar ventas.')
        return redirect('mi_caja')
    form = VentaForm(request.POST or None)
    lineas = LineasVentaFormSet(request.POST or None, prefix='lineas',
                                form_kwargs={'sucursal': request.user.sucursal_id})
    if request.method == 'POST' and form.is_valid() and lineas.is_valid():
        try:
            venta = servicios.registrar_venta(request.user, lineas=lineas.lineas('cantidad'), **form.cleaned_data)
        except ValidationError as error:
            for mensaje in error.messages:
                form.add_error(None, mensaje)
        else:
            messages.success(request, f'Venta {venta.numero} registrada.')
            return redirect('venta_detalle', pk=venta.pk)
    precios = {str(a.pk): str(a.precio_venta) for a in lineas.empty_form.fields['articulo'].queryset}
    return render(request, 'ventas/form.html', {'form': form, 'lineas': lineas, 'precios': precios})


@login_required
def detalle(request, pk):
    venta = get_object_or_404(Venta.objects.select_related('vendedor', 'sucursal', 'usuario_anulacion'), pk=pk)
    if not _puede_ver_venta(request.user, venta):
        raise PermissionDenied
    puede_anular = venta.estado == Venta.Estado.VIGENTE and request.user.has_perm('ventas.anular_venta')
    puede_cobrar = (venta.saldo > 0 and venta.estado == Venta.Estado.VIGENTE
                    and request.user.has_perm('ventas.registrar_venta'))
    return render(request, 'ventas/detalle.html', {
        'venta': venta, 'pagos': venta.pagos.select_related('usuario'),
        'detalles': venta.detalles.select_related('articulo').order_by('pk'), 'puede_anular': puede_anular,
        'pago_form': PagoForm(initial={'monto': venta.saldo}) if puede_cobrar else None,
    })


@require_POST
@login_required
@permission_required('ventas.registrar_venta', raise_exception=True)
def cobrar(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    form = PagoForm(request.POST)
    if form.is_valid():
        try:
            servicios.registrar_pago(venta, request.user, form.cleaned_data['monto'], form.cleaned_data['forma_pago'])
            messages.success(request, 'Pago registrado.')
        except ValidationError as error:
            messages.error(request, ' '.join(error.messages))
    else:
        messages.error(request, 'Revise el monto y la forma de pago.')
    return redirect('venta_detalle', pk=venta.pk)


@login_required
def nota(request, pk):
    """Nota de venta imprimible, con el vendedor en el encabezado."""
    venta = get_object_or_404(Venta.objects.select_related('vendedor', 'sucursal'), pk=pk)
    if not _puede_ver_venta(request.user, venta):
        raise PermissionDenied
    return render(request, 'ventas/nota.html', {
        'venta': venta, 'pagos': venta.pagos.all(), 'detalles': venta.detalles.select_related('articulo').order_by('pk'),
    })


@login_required
@permission_required('ventas.anular_venta', raise_exception=True)
def anular(request, pk):
    """Anula la venta con un motivo: repone el stock y devuelve lo pagado desde la caja de quien anula."""
    venta = get_object_or_404(Venta.objects.select_related('vendedor', 'sucursal'), pk=pk)
    if venta.estado != Venta.Estado.VIGENTE:
        messages.info(request, f'La {venta} ya está anulada.')
        return redirect('venta_detalle', pk=venta.pk)
    form = AnularForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            servicios.anular_venta(venta, request.user, form.cleaned_data['motivo'])
        except ValidationError as error:
            for mensaje in error.messages:
                form.add_error(None, mensaje)
        else:
            messages.success(request, f'La {venta} quedó anulada. El stock se repuso.')
            return redirect('venta_detalle', pk=venta.pk)
    return render(request, 'ventas/anular.html', {
        'venta': venta, 'form': form, 'tiene_caja': caja_abierta(request.user) is not None,
    })

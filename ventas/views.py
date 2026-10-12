from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from caja.servicios import caja_abierta

from . import servicios
from .forms import PagoForm, VentaForm
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
    if request.method == 'POST' and form.is_valid():
        try:
            venta = servicios.registrar_venta(request.user, **form.cleaned_data)
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f'Venta {venta.numero} registrada.')
            return redirect('venta_detalle', pk=venta.pk)
    return render(request, 'ventas/form.html', {'form': form})


@login_required
def detalle(request, pk):
    venta = get_object_or_404(Venta.objects.select_related('vendedor', 'sucursal'), pk=pk)
    if not _puede_ver_venta(request.user, venta):
        raise PermissionDenied
    puede_cobrar = (venta.saldo > 0 and venta.estado == Venta.Estado.VIGENTE
                    and request.user.has_perm('ventas.registrar_venta'))
    return render(request, 'ventas/detalle.html', {
        'venta': venta, 'pagos': venta.pagos.select_related('usuario'),
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
    return render(request, 'ventas/nota.html', {'venta': venta, 'pagos': venta.pagos.all()})

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import servicios
from .forms import AbrirCajaForm, CerrarCajaForm, MovimientoForm
from .models import SesionCaja


@login_required
@permission_required('caja.operar_caja', raise_exception=True)
def mi_caja(request):
    sesion = servicios.caja_abierta(request.user)
    contexto = {'sesion': sesion}
    if sesion:
        contexto.update(movimiento_form=MovimientoForm(), cerrar_form=CerrarCajaForm(),
                        movimientos=sesion.movimientos.all())
    else:
        contexto['abrir_form'] = AbrirCajaForm()
    contexto['cerradas'] = SesionCaja.objects.filter(
        usuario=request.user, estado=SesionCaja.Estado.CERRADA)[:10]
    return render(request, 'caja/mi_caja.html', contexto)


def _ejecutar(request, form_class, accion, exito):
    form = form_class(request.POST)
    if form.is_valid():
        try:
            accion(form.cleaned_data)
            messages.success(request, exito)
        except ValidationError as error:
            messages.error(request, ' '.join(error.messages))
    else:
        errores = [f'{form.fields[c].label or c}: {e}' if c in form.fields else e
                   for c, lista in form.errors.items() for e in lista]
        messages.error(request, ' '.join(errores))
    return redirect('mi_caja')


@require_POST
@login_required
@permission_required('caja.operar_caja', raise_exception=True)
def abrir(request):
    return _ejecutar(request, AbrirCajaForm, lambda d: servicios.abrir_caja(
        request.user, d['monto_inicial'], d['observacion']), 'Caja abierta.')


@require_POST
@login_required
@permission_required('caja.operar_caja', raise_exception=True)
def movimiento(request):
    return _ejecutar(request, MovimientoForm, lambda d: servicios.registrar_movimiento(
        request.user, d['tipo'], d['forma_pago'], d['monto'], d['concepto']), 'Movimiento registrado.')


@require_POST
@login_required
@permission_required('caja.operar_caja', raise_exception=True)
def cerrar(request):
    return _ejecutar(request, CerrarCajaForm, lambda d: servicios.cerrar_caja(
        request.user, d['monto_contado'], d['observacion']), 'Caja cerrada. Revise el arqueo en el historial.')


@login_required
def detalle(request, pk):
    sesion = get_object_or_404(SesionCaja.objects.select_related('usuario', 'sucursal'), pk=pk)
    if sesion.usuario != request.user and not request.user.has_perm('caja.ver_todas_cajas'):
        raise PermissionDenied
    return render(request, 'caja/detalle.html', {'sesion': sesion, 'movimientos': sesion.movimientos.all()})


@login_required
@permission_required('caja.ver_todas_cajas', raise_exception=True)
def todas(request):
    sesiones = SesionCaja.objects.select_related('usuario', 'sucursal')[:100]
    return render(request, 'caja/todas.html', {'sesiones': sesiones})

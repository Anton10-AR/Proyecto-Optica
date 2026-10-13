"""Vistas a nivel de proyecto que combinan datos de varias apps."""

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from asistencia.models import Marcacion
from asistencia.servicios import proximo_tipo
from caja.servicios import caja_abierta
from core.models import RegistroActividad
from ventas.models import Venta


@login_required
def inicio(request):
    """Panel de inicio: cada bloque se muestra solo si el rol tiene el permiso correspondiente."""
    usuario = request.user
    hoy = timezone.localdate()
    contexto = {'hoy': hoy}

    if usuario.has_perm('asistencia.marcar_asistencia'):
        contexto['marcaciones_hoy'] = list(
            Marcacion.objects.filter(usuario=usuario, fecha_hora__date=hoy).order_by('fecha_hora'))
        contexto['proximo_tipo'] = proximo_tipo(usuario)

    if usuario.has_perm('caja.operar_caja'):
        contexto['mi_caja'] = caja_abierta(usuario)

    if usuario.has_perm('ventas.registrar_venta'):
        mias = Venta.objects.filter(vendedor=usuario, fecha__date=hoy, estado=Venta.Estado.VIGENTE)
        contexto['mis_ventas_hoy'] = mias.aggregate(cantidad=Count('id'), total=Sum('total'))

    if usuario.has_perm('ventas.ver_todas_ventas'):
        todas = Venta.objects.filter(fecha__date=hoy, estado=Venta.Estado.VIGENTE)
        contexto['ventas_hoy'] = todas.aggregate(cantidad=Count('id'), total=Sum('total'))

    if usuario.has_perm('asistencia.ver_todas_marcaciones'):
        activos = get_user_model().objects.filter(is_active=True, sucursal__isnull=False)
        contexto['personal'] = {
            'total': activos.count(),
            'presentes': activos.filter(
                marcaciones__fecha_hora__date=hoy, marcaciones__tipo=Marcacion.Tipo.ENTRADA).distinct().count(),
        }

    if usuario.has_perm('core.view_usuario'):
        contexto['usuarios'] = get_user_model().objects.aggregate(
            activos=Count('id', filter=Q(is_active=True)), inactivos=Count('id', filter=Q(is_active=False)))

    if usuario.has_perm('core.view_registroactividad'):
        contexto['fallidos_hoy'] = RegistroActividad.objects.filter(
            accion=RegistroActividad.Accion.INICIO_FALLIDO, fecha__date=hoy).count()
        contexto['actividad'] = RegistroActividad.objects.select_related('usuario', 'usuario_afectado')[:6]

    return render(request, 'inicio.html', contexto)

from datetime import date

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils import timezone

from . import servicios
from .forms import MarcacionForm
from .models import Marcacion


@login_required
@permission_required('asistencia.marcar_asistencia', raise_exception=True)
def marcar(request):
    if request.method == 'POST':
        form = MarcacionForm(request.POST)
        if form.is_valid():
            try:
                marcacion = servicios.registrar_marcacion(
                    request.user, form.cleaned_data['latitud'], form.cleaned_data['longitud'])
            except ValidationError as error:
                messages.error(request, ' '.join(error.messages))
            else:
                hora = timezone.localtime(marcacion.fecha_hora)
                messages.success(request, f'{marcacion.get_tipo_display()} registrada a las {hora:%H:%M}.')
        else:
            messages.error(request, 'No se recibió una ubicación válida. Permita el acceso a la ubicación.')
        return redirect('asistencia_marcar')
    hoy = Marcacion.objects.filter(usuario=request.user, fecha_hora__date=timezone.localdate())
    return render(request, 'asistencia/marcar.html', {
        'proximo': servicios.proximo_tipo(request.user), 'hoy': hoy.order_by('fecha_hora'),
    })


@login_required
@permission_required('asistencia.marcar_asistencia', raise_exception=True)
def mi_historial(request):
    marcaciones = Marcacion.objects.filter(usuario=request.user).select_related('sucursal')
    pagina = Paginator(marcaciones, 30).get_page(request.GET.get('pagina'))
    return render(request, 'asistencia/historial.html', {'pagina': pagina, 'personal': True})


@login_required
@permission_required('asistencia.ver_todas_marcaciones', raise_exception=True)
def todas(request):
    marcaciones = Marcacion.objects.select_related('usuario', 'sucursal')
    usuario_id = request.GET.get('usuario', '')
    fecha = request.GET.get('fecha', '')
    if usuario_id:
        marcaciones = marcaciones.filter(usuario_id=usuario_id)
    if fecha:
        try:
            marcaciones = marcaciones.filter(fecha_hora__date=date.fromisoformat(fecha))
        except ValueError:
            messages.error(request, 'Fecha inválida.')
    pagina = Paginator(marcaciones, 30).get_page(request.GET.get('pagina'))
    return render(request, 'asistencia/historial.html', {
        'pagina': pagina, 'personal': False, 'usuario_id': usuario_id, 'fecha': fecha,
        'usuarios': get_user_model().objects.order_by('first_name', 'last_name'),
    })

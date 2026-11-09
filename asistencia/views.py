import csv
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import calculo, servicios
from .forms import AsignacionForm, AusenciaForm, CargoForm, FeriadoForm, HorarioForm, MarcacionForm, ReporteForm
from .models import Ausencia, Feriado, Horario, Marcacion
from .templatetags.asistencia import duracion


# ---------- Marcación y consulta propia ----------

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
    hoy = timezone.localdate()
    horario = calculo.horario_vigente(request.user, hoy)
    return render(request, 'asistencia/marcar.html', {
        'proximo': servicios.proximo_tipo(request.user),
        'hoy': Marcacion.objects.filter(usuario=request.user, fecha_hora__date=hoy).order_by('fecha_hora'),
        'horario': horario, 'tramos_hoy': horario.tramos_por_dia().get(hoy.weekday(), []) if horario else [],
        'feriado_hoy': Feriado.objects.filter(fecha=hoy).first(),
    })


@login_required
@permission_required('asistencia.marcar_asistencia', raise_exception=True)
def mi_historial(request):
    marcaciones = Marcacion.objects.filter(usuario=request.user).select_related('sucursal')
    pagina = Paginator(marcaciones, 30).get_page(request.GET.get('pagina'))
    return render(request, 'asistencia/historial.html', {'pagina': pagina, 'personal': True})


@login_required
@permission_required('asistencia.marcar_asistencia', raise_exception=True)
def mi_asistencia(request):
    """El empleado consulta sus atrasos, faltas y horas del período (RF19)."""
    return _detalle_empleado(request, request.user, propio=True)


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


# ---------- Reportes (RF19, RF20) ----------

def _csv(nombre, encabezados, filas):
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre}.csv"'
    respuesta.write('﻿')  # BOM: Excel abre el archivo como UTF-8.
    escritor = csv.writer(respuesta, delimiter=';')
    escritor.writerow(encabezados)
    escritor.writerows(filas)
    return respuesta


def _filtros(request, desde, hasta, sucursal=None):
    return f'desde={desde:%Y-%m-%d}&hasta={hasta:%Y-%m-%d}' + (f'&sucursal={sucursal.pk}' if sucursal else '')


@login_required
@permission_required('asistencia.ver_todas_marcaciones', raise_exception=True)
def reporte(request):
    """Asistencia, atrasos y faltas por empleado, sucursal y período (RF20)."""
    form = ReporteForm(request.GET or None)
    desde, hasta, sucursal = form.periodo()
    resumenes = list(calculo.calcular(calculo.personal(sucursal), desde, hasta).values())
    if request.GET.get('formato') == 'csv':
        filas = [[r.usuario.get_full_name(), r.usuario.cargo, r.usuario.sucursal, r.laborables, r.asistidos, r.faltas,
                  r.atrasos, r.minutos_atraso, r.tramos_sin_marcar, r.ausencias, r.feriados, duracion(r.horas)]
                 for r in resumenes]
        return _csv(f'asistencia_{desde:%Y-%m-%d}_a_{hasta:%Y-%m-%d}',
                    ['Empleado', 'Cargo', 'Sucursal', 'Días laborables', 'Asistidos', 'Faltas', 'Atrasos',
                     'Minutos de atraso', 'Tramos sin marcar', 'Días de permiso o vacación', 'Feriados',
                     'Horas trabajadas'], filas)
    totales = {campo: sum(getattr(r, campo) for r in resumenes)
               for campo in ('laborables', 'asistidos', 'faltas', 'atrasos', 'minutos_atraso', 'tramos_sin_marcar',
                             'ausencias')}
    return render(request, 'asistencia/reporte.html', {
        'form': form, 'resumenes': resumenes, 'desde': desde, 'hasta': min(hasta, timezone.localdate()),
        'sucursal': sucursal, 'totales': totales, 'filtros': _filtros(request, desde, hasta, sucursal),
        'total_horas': sum((r.horas for r in resumenes), timedelta()),
    })


@login_required
@permission_required('asistencia.ver_todas_marcaciones', raise_exception=True)
def reporte_empleado(request, pk):
    usuario = get_object_or_404(get_user_model(), pk=pk)
    return _detalle_empleado(request, usuario, propio=False)


def _detalle_empleado(request, usuario, propio):
    form = ReporteForm(request.GET or None)
    desde, hasta, _ = form.periodo()
    resumen = calculo.calcular([usuario], desde, hasta)[usuario.pk]
    if request.GET.get('formato') == 'csv':
        filas = [[f'{d.fecha:%d/%m/%Y}', d.etiqueta,
                  ' / '.join(f'{t.inicio:%H:%M}–{t.fin:%H:%M}' for t in d.tramos),
                  ' / '.join(f'{timezone.localtime(m.fecha_hora):%H:%M} {m.get_tipo_display().lower()}'
                             for m in d.marcaciones),
                  d.atraso, d.tramos_sin_marcar, duracion(d.horas)] for d in resumen.dias]
        return _csv(f'asistencia_{usuario.username}_{desde:%Y-%m-%d}_a_{hasta:%Y-%m-%d}',
                    ['Fecha', 'Estado', 'Horario', 'Marcaciones', 'Minutos de atraso', 'Tramos sin marcar',
                     'Horas trabajadas'], filas)
    return render(request, 'asistencia/reporte_empleado.html', {
        'form': form, 'empleado': usuario, 'resumen': resumen, 'dias': list(reversed(resumen.dias)),
        'propio': propio, 'desde': desde, 'hasta': min(hasta, timezone.localdate()),
        'horario': calculo.horario_vigente(usuario), 'filtros': _filtros(request, desde, hasta),
    })


# ---------- Personal y horarios (RF17, RF26) ----------

@login_required
@permission_required('asistencia.gestionar_horarios', raise_exception=True)
def personal_lista(request):
    hoy = timezone.localdate()
    empleados = [(u, calculo.horario_vigente(u, hoy)) for u in calculo.personal()]
    return render(request, 'asistencia/personal/lista.html', {'empleados': empleados})


@login_required
@permission_required('asistencia.gestionar_horarios', raise_exception=True)
def empleado_ficha(request, pk):
    usuario = get_object_or_404(get_user_model().objects.select_related('sucursal', 'rol'), pk=pk)
    accion = request.POST.get('accion') if request.method == 'POST' else None
    cargo_form = CargoForm(request.POST if accion == 'cargo' else None, instance=usuario, prefix='cargo')
    asignar_form = AsignacionForm(request.POST if accion == 'asignar' else None, usuario=usuario,
                                  registrado_por=request.user, prefix='asignar')
    if accion == 'cargo' and cargo_form.is_valid():
        cargo_form.save()
        messages.success(request, f'Se actualizó el cargo de {usuario}.')
        return redirect('empleado_ficha', pk=pk)
    if accion == 'asignar' and asignar_form.is_valid():
        asignacion = asignar_form.save()
        messages.success(request, f'{usuario} tiene el horario «{asignacion.horario}» desde el '
                                  f'{asignacion.desde:%d/%m/%Y}.')
        return redirect('empleado_ficha', pk=pk)
    hoy = timezone.localdate()
    asignaciones = list(usuario.asignaciones_horario.select_related('horario', 'registrado_por'))
    return render(request, 'asistencia/personal/ficha.html', {
        'empleado': usuario, 'cargo_form': cargo_form, 'asignar_form': asignar_form, 'hoy': hoy,
        'asignaciones': asignaciones, 'vigente': next((a for a in asignaciones if a.desde <= hoy), None),
    })


@login_required
@permission_required('asistencia.gestionar_horarios', raise_exception=True)
def horario_lista(request):
    horarios = Horario.objects.prefetch_related('tramos')
    return render(request, 'asistencia/horarios/lista.html', {'horarios': horarios})


@login_required
@permission_required('asistencia.gestionar_horarios', raise_exception=True)
def horario_form(request, pk=None):
    horario = get_object_or_404(Horario, pk=pk) if pk else None
    form = HorarioForm(request.POST or None, instance=horario)
    if request.method == 'POST' and form.is_valid():
        horario = form.save()
        messages.success(request, f'Se guardó el horario «{horario}».')
        return redirect('horario_lista')
    return render(request, 'asistencia/horarios/form.html', {
        'form': form, 'horario': horario,
        'asignados': horario.asignaciones.values('usuario').distinct().count() if horario else 0,
    })


# ---------- Permisos, vacaciones y feriados (RF27, RF28) ----------

@login_required
@permission_required('asistencia.gestionar_ausencias', raise_exception=True)
def ausencia_lista(request):
    form = AusenciaForm(request.POST or None, registrado_por=request.user)
    if request.method == 'POST' and form.is_valid():
        ausencia = form.save()
        messages.success(request, f'Se registró: {ausencia}.')
        return redirect('ausencia_lista')
    ausencias = Ausencia.objects.select_related('usuario', 'registrado_por')
    pagina = Paginator(ausencias, 25).get_page(request.GET.get('pagina'))
    return render(request, 'asistencia/ausencias.html', {'form': form, 'pagina': pagina, 'hoy': timezone.localdate()})


@require_POST
@login_required
@permission_required('asistencia.gestionar_ausencias', raise_exception=True)
def ausencia_eliminar(request, pk):
    ausencia = get_object_or_404(Ausencia, pk=pk)
    ausencia.delete()
    messages.success(request, f'Se eliminó: {ausencia}. Esos días vuelven a calcularse con normalidad.')
    return redirect('ausencia_lista')


@login_required
@permission_required('asistencia.gestionar_feriados', raise_exception=True)
def feriado_lista(request):
    hoy = timezone.localdate()
    anio = int(request.GET['anio']) if request.GET.get('anio', '').isdigit() else hoy.year
    form = FeriadoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        feriado = form.save()
        messages.success(request, f'Se registró el feriado {feriado}.')
        return redirect(f'{request.path}?anio={feriado.fecha.year}')
    return render(request, 'asistencia/feriados.html', {
        'form': form, 'anio': anio, 'feriados': Feriado.objects.filter(fecha__year=anio),
        'anios': sorted({anio, hoy.year, hoy.year + 1, *(d.year for d in Feriado.objects.dates('fecha', 'year'))}),
    })


@require_POST
@login_required
@permission_required('asistencia.gestionar_feriados', raise_exception=True)
def feriado_eliminar(request, pk):
    feriado = get_object_or_404(Feriado, pk=pk)
    feriado.delete()
    messages.success(request, f'Se eliminó el feriado {feriado}.')
    return redirect(f'{reverse("feriado_lista")}?anio={feriado.fecha.year}')

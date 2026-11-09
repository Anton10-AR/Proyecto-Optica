"""Cálculo de la asistencia (RF19): atrasos, faltas y horas trabajadas por día.

Parte del horario vigente de cada empleado, sus marcaciones, sus permisos y vacaciones, y los feriados.
Es de solo lectura: no guarda nada, así que un cambio de tolerancia o un permiso registrado después
se reflejan en el siguiente cálculo.

Reglas:
- Cada tramo del horario toma como entrada la primera marcación de entrada desde la mitad del descanso
  anterior (o desde el inicio del día) hasta el fin del tramo.
- Si la entrada supera la tolerancia, el atraso se cuenta desde la hora del horario; si no, es puntual.
- Falta: un día laborable (con tramos, sin feriado ni permiso) sin ninguna entrada. Si se marca un tramo
  pero no otro, el día cuenta como asistido y el tramo se informa como «sin marcar».
- Horas trabajadas: la suma de los intervalos entrada → salida del día, con o sin horario.
"""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Configuracion

from .models import AsignacionHorario, Ausencia, Feriado, Marcacion


class EstadoDia:
    ASISTIO = 'ASISTIO'
    FALTA = 'FALTA'
    EN_CURSO = 'EN_CURSO'
    FERIADO = 'FERIADO'
    AUSENCIA = 'AUSENCIA'
    DESCANSO = 'DESCANSO'
    ETIQUETAS = {ASISTIO: 'Asistió', FALTA: 'Falta', EN_CURSO: 'En curso', FERIADO: 'Feriado',
                 AUSENCIA: 'Permiso o vacación', DESCANSO: 'Descanso'}


class EstadoTramo:
    PUNTUAL = 'PUNTUAL'
    ATRASO = 'ATRASO'
    SIN_MARCAR = 'SIN_MARCAR'
    PENDIENTE = 'PENDIENTE'


@dataclass
class TramoDia:
    inicio: datetime
    fin: datetime
    entrada: datetime | None
    estado: str
    atraso: int = 0  # minutos


@dataclass
class Dia:
    fecha: object
    estado: str
    programado: bool  # el horario tenía tramos ese día
    tramos: list = field(default_factory=list)
    marcaciones: list = field(default_factory=list)
    horas: timedelta = timedelta()
    salida_sin_marcar: bool = False
    detalle: str = ''  # nombre del feriado o tipo de permiso

    @property
    def etiqueta(self):
        return self.detalle if self.estado in (EstadoDia.FERIADO, EstadoDia.AUSENCIA) else EstadoDia.ETIQUETAS[self.estado]

    @property
    def atraso(self):
        return sum(t.atraso for t in self.tramos)

    @property
    def tramos_sin_marcar(self):
        return sum(1 for t in self.tramos if t.estado == EstadoTramo.SIN_MARCAR) if self.estado == EstadoDia.ASISTIO else 0


@dataclass
class Resumen:
    usuario: object
    dias: list
    con_horario: bool

    def _contar(self, estado, programado=None):
        return sum(1 for d in self.dias if d.estado == estado and (programado is None or d.programado == programado))

    @property
    def laborables(self):
        return self.asistidos + self.faltas

    @property
    def asistidos(self):
        return self._contar(EstadoDia.ASISTIO, programado=True)

    @property
    def faltas(self):
        return self._contar(EstadoDia.FALTA)

    @property
    def atrasos(self):
        return sum(1 for d in self.dias for t in d.tramos if t.estado == EstadoTramo.ATRASO)

    @property
    def minutos_atraso(self):
        return sum(d.atraso for d in self.dias)

    @property
    def tramos_sin_marcar(self):
        return sum(d.tramos_sin_marcar for d in self.dias)

    @property
    def salidas_sin_marcar(self):
        return sum(1 for d in self.dias if d.salida_sin_marcar)

    @property
    def horas(self):
        return sum((d.horas for d in self.dias), timedelta())

    @property
    def ausencias(self):
        """Días laborables cubiertos por permisos, vacaciones o bajas médicas."""
        return self._contar(EstadoDia.AUSENCIA, programado=True)

    @property
    def feriados(self):
        """Feriados que cayeron en días laborables del empleado."""
        return self._contar(EstadoDia.FERIADO, programado=True)


def _momento(fecha, hora):
    return timezone.make_aware(datetime.combine(fecha, hora))


def _horas(marcaciones, es_hoy):
    """Suma los intervalos entrada → salida. Una entrada sin salida en un día pasado se informa."""
    total, abierta = timedelta(), None
    for m in marcaciones:
        if m.tipo == Marcacion.Tipo.ENTRADA:
            abierta = m.fecha_hora
        elif abierta is not None:
            total += m.fecha_hora - abierta
            abierta = None
    return total, abierta is not None and not es_hoy


def calcular_dia(fecha, tramos_horario, marcaciones, tolerancia, ahora, feriado=None, ausencia=None):
    """Estado de un día. `tramos_horario` son los TramoHorario del día de la semana; `marcaciones`, las del día
    en orden cronológico."""
    horas, salida_sin_marcar = _horas(marcaciones, fecha == timezone.localdate(ahora))
    dia = Dia(fecha=fecha, estado=EstadoDia.DESCANSO, programado=bool(tramos_horario), marcaciones=marcaciones,
              horas=horas, salida_sin_marcar=salida_sin_marcar)
    if feriado:
        dia.estado, dia.detalle = EstadoDia.FERIADO, feriado
        return dia
    if ausencia:
        dia.estado, dia.detalle = EstadoDia.AUSENCIA, ausencia.get_tipo_display()
        return dia
    if not tramos_horario:
        return dia

    entradas = [m.fecha_hora for m in marcaciones if m.tipo == Marcacion.Tipo.ENTRADA]
    fin_anterior = None
    for t in tramos_horario:
        inicio, fin = _momento(fecha, t.hora_entrada), _momento(fecha, t.hora_salida)
        desde = fin_anterior + (inicio - fin_anterior) / 2 if fin_anterior else _momento(fecha, time.min)
        entrada = next((e for e in entradas if desde <= e < fin), None)
        if entrada:
            minutos = max(0, int((entrada - inicio).total_seconds() // 60))
            if minutos > tolerancia:
                tramo = TramoDia(inicio, fin, entrada, EstadoTramo.ATRASO, minutos)
            else:
                tramo = TramoDia(inicio, fin, entrada, EstadoTramo.PUNTUAL)
        else:
            tramo = TramoDia(inicio, fin, None, EstadoTramo.PENDIENTE if ahora < fin else EstadoTramo.SIN_MARCAR)
        dia.tramos.append(tramo)
        fin_anterior = fin

    if any(t.entrada for t in dia.tramos):
        dia.estado = EstadoDia.ASISTIO
    elif any(t.estado == EstadoTramo.PENDIENTE for t in dia.tramos):
        dia.estado = EstadoDia.EN_CURSO
    else:
        dia.estado = EstadoDia.FALTA
    return dia


def calcular(usuarios, desde, hasta, ahora=None):
    """{pk del usuario: Resumen} con un Dia por fecha entre `desde` y `hasta` (sin pasar de hoy)."""
    ahora = ahora or timezone.now()
    hasta = min(hasta, timezone.localdate(ahora))
    usuarios = list(usuarios)
    ids = [u.pk for u in usuarios]
    tolerancia = Configuracion.actual().tolerancia_minutos
    feriados = dict(Feriado.objects.filter(fecha__range=(desde, hasta)).values_list('fecha', 'nombre'))

    asignaciones, ausencias, marcaciones = {}, {}, {}
    for a in (AsignacionHorario.objects.filter(usuario_id__in=ids, desde__lte=hasta)
              .select_related('horario').prefetch_related('horario__tramos').order_by('desde')):
        asignaciones.setdefault(a.usuario_id, []).append(a)
    for a in Ausencia.objects.filter(usuario_id__in=ids, desde__lte=hasta, hasta__gte=desde):
        ausencias.setdefault(a.usuario_id, []).append(a)
    inicio, fin = _momento(desde, time.min), _momento(hasta + timedelta(days=1), time.min)
    for m in Marcacion.objects.filter(usuario_id__in=ids, fecha_hora__gte=inicio, fecha_hora__lt=fin).order_by('fecha_hora'):
        marcaciones.setdefault((m.usuario_id, timezone.localdate(m.fecha_hora)), []).append(m)

    resumenes = {}
    for usuario in usuarios:
        propias = asignaciones.get(usuario.pk, [])
        dias, fecha = [], desde
        while fecha <= hasta:
            vigente = next((a for a in reversed(propias) if a.desde <= fecha), None)
            tramos = vigente.horario.tramos_por_dia().get(fecha.weekday(), []) if vigente else []
            ausencia = next((a for a in ausencias.get(usuario.pk, []) if a.desde <= fecha <= a.hasta), None)
            dias.append(calcular_dia(fecha, tramos, marcaciones.get((usuario.pk, fecha), []), tolerancia, ahora,
                                     feriados.get(fecha), ausencia))
            fecha += timedelta(days=1)
        resumenes[usuario.pk] = Resumen(usuario, dias, con_horario=bool(propias))
    return resumenes


def personal(sucursal=None):
    """Empleados activos con sucursal: son quienes marcan asistencia."""
    usuarios = get_user_model().objects.filter(is_active=True, sucursal__isnull=False).select_related('sucursal')
    if sucursal:
        usuarios = usuarios.filter(sucursal=sucursal)
    return usuarios.order_by('first_name', 'last_name')


def horario_vigente(usuario, fecha=None):
    fecha = fecha or timezone.localdate()
    asignacion = (AsignacionHorario.objects.filter(usuario=usuario, desde__lte=fecha)
                  .select_related('horario').order_by('-desde').first())
    return asignacion.horario if asignacion else None

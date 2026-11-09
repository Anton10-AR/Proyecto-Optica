from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower

from core.models import Sucursal

DIAS_SEMANA = [(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'),
               (6, 'Domingo')]


class Marcacion(models.Model):
    """Registro de entrada o salida (check-in / check-out) de un usuario."""

    class Tipo(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SALIDA = 'SALIDA', 'Salida'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='marcaciones',
    )
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='marcaciones')
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    fecha_hora = models.DateTimeField(auto_now_add=True, db_index=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    distancia_metros = models.PositiveIntegerField(help_text='Distancia a la sucursal al marcar.')

    class Meta:
        verbose_name = 'marcación'
        verbose_name_plural = 'marcaciones'
        ordering = ['-fecha_hora']
        permissions = [
            ('marcar_asistencia', 'Puede marcar su propia asistencia y ver su historial'),
            ('ver_todas_marcaciones', 'Puede ver la asistencia y los reportes de todo el personal'),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} · {self.usuario} · {self.fecha_hora:%d/%m/%Y %H:%M}'


class Horario(models.Model):
    """Horario laboral semanal. Cada día puede tener varios tramos (horario partido, RF17)."""

    nombre = models.CharField(max_length=80)
    descripcion = models.CharField('descripción', max_length=200, blank=True)
    activo = models.BooleanField(default=True, help_text='Un horario inactivo no se ofrece para nuevas asignaciones.')

    class Meta:
        verbose_name = 'horario'
        verbose_name_plural = 'horarios'
        ordering = ['nombre']
        constraints = [models.UniqueConstraint(Lower('nombre'), name='horario_nombre_unico',
                                               violation_error_message='Ya existe un horario con este nombre.')]
        permissions = [('gestionar_horarios', 'Puede gestionar los horarios, asignarlos y editar el cargo del personal')]

    def __str__(self):
        return self.nombre

    def tramos_por_dia(self):
        """{día de la semana: [tramos ordenados]}."""
        dias = {}
        for tramo in self.tramos.all():
            dias.setdefault(tramo.dia_semana, []).append(tramo)
        return dias

    def dias(self):
        """[(nombre del día, [tramos]), ...] de lunes a domingo, para mostrar el horario."""
        por_dia = self.tramos_por_dia()
        return [(nombre, por_dia.get(dia, [])) for dia, nombre in DIAS_SEMANA]


class TramoHorario(models.Model):
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='tramos')
    dia_semana = models.PositiveSmallIntegerField('día', choices=DIAS_SEMANA)
    hora_entrada = models.TimeField('entrada')
    hora_salida = models.TimeField('salida')

    class Meta:
        verbose_name = 'tramo del horario'
        verbose_name_plural = 'tramos del horario'
        ordering = ['dia_semana', 'hora_entrada']
        constraints = [models.CheckConstraint(condition=Q(hora_entrada__lt=F('hora_salida')),
                                              name='tramo_entrada_antes_de_salida')]

    def __str__(self):
        return f'{self.get_dia_semana_display()} {self.hora_entrada:%H:%M}–{self.hora_salida:%H:%M}'


class AsignacionHorario(models.Model):
    """Horario de un empleado desde una fecha. Vale hasta la siguiente asignación, así los días pasados
    se calculan con el horario que tenían."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='asignaciones_horario')
    horario = models.ForeignKey(Horario, on_delete=models.PROTECT, related_name='asignaciones')
    desde = models.DateField('vigente desde')
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'asignación de horario'
        verbose_name_plural = 'asignaciones de horario'
        ordering = ['-desde']
        constraints = [models.UniqueConstraint(fields=['usuario', 'desde'], name='asignacion_usuario_desde_unica')]

    def __str__(self):
        return f'{self.usuario} · {self.horario} desde {self.desde:%d/%m/%Y}'


class Ausencia(models.Model):
    """Permiso, vacación o baja médica por días completos. Esos días no cuentan como falta (RF27)."""

    class Tipo(models.TextChoices):
        PERMISO = 'PERMISO', 'Permiso'
        VACACION = 'VACACION', 'Vacación'
        BAJA_MEDICA = 'BAJA_MEDICA', 'Baja médica'

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ausencias',
                                verbose_name='empleado')
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    desde = models.DateField()
    hasta = models.DateField()
    motivo = models.CharField(max_length=255, blank=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'permiso o vacación'
        verbose_name_plural = 'permisos y vacaciones'
        ordering = ['-desde']
        constraints = [models.CheckConstraint(condition=Q(desde__lte=F('hasta')), name='ausencia_desde_antes_de_hasta')]
        permissions = [('gestionar_ausencias', 'Puede registrar permisos y vacaciones del personal')]

    def __str__(self):
        return f'{self.get_tipo_display()} · {self.usuario} · {self.desde:%d/%m/%Y}–{self.hasta:%d/%m/%Y}'

    def clean(self):
        if self.desde and self.hasta:
            if self.desde > self.hasta:
                raise ValidationError({'hasta': 'Debe ser igual o posterior a la fecha de inicio.'})
            if self.usuario_id and Ausencia.objects.filter(
                    usuario_id=self.usuario_id, desde__lte=self.hasta, hasta__gte=self.desde).exclude(pk=self.pk).exists():
                raise ValidationError('El empleado ya tiene un permiso o vacación que se cruza con esas fechas.')

    @property
    def dias(self):
        return (self.hasta - self.desde).days + 1


class Feriado(models.Model):
    """Día no laborable para todas las sucursales (RF28)."""

    fecha = models.DateField(unique=True, error_messages={'unique': 'Ya hay un feriado en esa fecha.'})
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'feriado'
        verbose_name_plural = 'feriados'
        ordering = ['fecha']
        permissions = [('gestionar_feriados', 'Puede gestionar el calendario de feriados')]

    def __str__(self):
        return f'{self.fecha:%d/%m/%Y} · {self.nombre}'

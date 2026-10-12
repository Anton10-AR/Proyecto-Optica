from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

validar_ci = RegexValidator(
    r'^\d{5,10}(-[0-9A-Z]{1,2})?$',
    'Ingrese un CI válido: de 5 a 10 dígitos y, si corresponde, el complemento (ej. 1234567-1B).',
)
validar_telefono = RegexValidator(
    r'^(\+591)?[2-7]\d{6,7}$',
    'Ingrese un teléfono válido: 7 u 8 dígitos, opcionalmente con el prefijo +591.',
)


class Sucursal(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField('dirección', max_length=200)
    latitud = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitud = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    radio_metros = models.PositiveIntegerField(
        'radio permitido (m)', default=100,
        help_text='Distancia máxima a la sucursal para aceptar una marcación de asistencia.',
    )
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'sucursal'
        verbose_name_plural = 'sucursales'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    """Usuario del sistema. Todo el personal de la óptica es un usuario.

    El rol es un Group de Django (tabla auth_group); sus permisos están en
    auth_group_permissions. `rol` es la relación 1:N que usa la aplicación y se
    sincroniza con `groups` al guardar, que es lo que Django consulta para los permisos.
    """

    email = models.EmailField('correo electrónico', blank=True)
    ci = models.CharField(
        'CI', max_length=13, unique=True, null=True, blank=True, validators=[validar_ci],
    )
    telefono = models.CharField('teléfono', max_length=13, blank=True, validators=[validar_telefono])
    rol = models.ForeignKey(
        Group, on_delete=models.PROTECT, null=True, blank=True, related_name='usuarios',
    )
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT, null=True, blank=True, related_name='usuarios',
    )
    debe_cambiar_clave = models.BooleanField(
        default=False,
        help_text='Obliga a cambiar la contraseña en el próximo inicio de sesión.',
    )

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        ordering = ['first_name', 'last_name']
        constraints = [
            models.UniqueConstraint(
                Lower('email'), condition=~Q(email=''), name='usuario_email_unico',
                violation_error_message='Ya existe un usuario con este correo.',
            ),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # El rol de la aplicación es la fuente de verdad de los grupos del usuario.
        actuales = set(self.groups.values_list('pk', flat=True))
        esperados = {self.rol_id} if self.rol_id else set()
        if actuales != esperados:
            self.groups.set(esperados)

    def __str__(self):
        return self.get_full_name() or self.username


class RegistroActividad(models.Model):
    """Log de auditoría de acciones clave sobre cuentas de usuario."""

    class Accion(models.TextChoices):
        INICIO_SESION = 'INICIO_SESION', 'Inicio de sesión'
        INICIO_FALLIDO = 'INICIO_FALLIDO', 'Inicio de sesión fallido'
        CIERRE_SESION = 'CIERRE_SESION', 'Cierre de sesión'
        CAMBIO_CLAVE = 'CAMBIO_CLAVE', 'Cambio de contraseña'
        RESETEO_CLAVE = 'RESETEO_CLAVE', 'Reseteo de contraseña'
        CREACION_USUARIO = 'CREACION_USUARIO', 'Creación de usuario'
        ACTUALIZACION_USUARIO = 'ACTUALIZACION_USUARIO', 'Actualización de usuario'
        DESACTIVACION_USUARIO = 'DESACTIVACION_USUARIO', 'Desactivación de usuario'
        REACTIVACION_USUARIO = 'REACTIVACION_USUARIO', 'Reactivación de usuario'

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    accion = models.CharField(max_length=30, choices=Accion.choices)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, null=True, blank=True, related_name='actividades',
        help_text='Quién realizó la acción (vacío en un inicio de sesión fallido).',
    )
    usuario_afectado = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, null=True, blank=True, related_name='actividades_recibidas',
    )
    credencial = models.CharField(
        max_length=150, blank=True, help_text='Usuario o correo ingresado en un intento fallido.',
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    detalle = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'registro de actividad'
        verbose_name_plural = 'registros de actividad'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.fecha:%d/%m/%Y %H:%M} · {self.get_accion_display()}'

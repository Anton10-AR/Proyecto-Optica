from django.conf import settings
from django.db import models

from core.models import Sucursal


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
            ('ver_todas_marcaciones', 'Puede ver las marcaciones de todo el personal'),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} · {self.usuario} · {self.fecha_hora:%d/%m/%Y %H:%M}'

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum

from core.models import Sucursal

MONTO_POSITIVO = [MinValueValidator(Decimal('0.01'))]


class FormaPago(models.TextChoices):
    EFECTIVO = 'EFECTIVO', 'Efectivo'
    QR = 'QR', 'QR'
    TARJETA = 'TARJETA', 'Tarjeta'


class SesionCaja(models.Model):
    """Turno de caja de un usuario: apertura, movimientos y cierre con arqueo."""

    class Estado(models.TextChoices):
        ABIERTA = 'ABIERTA', 'Abierta'
        CERRADA = 'CERRADA', 'Cerrada'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sesiones_caja',
    )
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='sesiones_caja')
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ABIERTA)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    monto_inicial = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))],
    )
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_esperado = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Efectivo que debería haber al cierre, calculado por el sistema.',
    )
    monto_contado = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Efectivo contado físicamente en el arqueo.',
    )
    observacion = models.CharField('observación', max_length=255, blank=True)

    class Meta:
        verbose_name = 'sesión de caja'
        verbose_name_plural = 'sesiones de caja'
        ordering = ['-fecha_apertura']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario'], condition=Q(estado='ABIERTA'), name='una_caja_abierta_por_usuario',
                violation_error_message='El usuario ya tiene una caja abierta.',
            ),
        ]
        permissions = [
            ('operar_caja', 'Puede abrir su caja, registrar movimientos y cerrarla'),
            ('ver_todas_cajas', 'Puede ver las cajas de todos los usuarios'),
        ]

    def __str__(self):
        return f'Caja #{self.pk} · {self.usuario} · {self.fecha_apertura:%d/%m/%Y}'

    def _total_efectivo(self, tipo):
        total = self.movimientos.filter(tipo=tipo, forma_pago=FormaPago.EFECTIVO).aggregate(t=Sum('monto'))['t']
        return total or Decimal('0')

    @property
    def efectivo_esperado(self):
        return (
            self.monto_inicial
            + self._total_efectivo(MovimientoCaja.Tipo.INGRESO)
            - self._total_efectivo(MovimientoCaja.Tipo.EGRESO)
        )

    @property
    def diferencia(self):
        if self.monto_contado is None or self.monto_esperado is None:
            return None
        return self.monto_contado - self.monto_esperado


class MovimientoCaja(models.Model):
    class Tipo(models.TextChoices):
        INGRESO = 'INGRESO', 'Ingreso'
        EGRESO = 'EGRESO', 'Egreso'

    sesion = models.ForeignKey(SesionCaja, on_delete=models.PROTECT, related_name='movimientos')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='movimientos_caja',
    )
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    forma_pago = models.CharField('forma de pago', max_length=10, choices=FormaPago.choices)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=MONTO_POSITIVO)
    concepto = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'movimiento de caja'
        verbose_name_plural = 'movimientos de caja'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} {self.monto} · {self.concepto}'

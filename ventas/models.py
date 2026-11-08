from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum

from django.core.validators import MinValueValidator

from caja.models import MONTO_POSITIVO, FormaPago, MovimientoCaja
from core.models import Sucursal
from inventario.models import Articulo


class Venta(models.Model):
    """Nota de venta: encabezado, detalle de artículos (DetalleVenta) y pagos.

    El total es la suma de las líneas menos el descuento. Las ventas registradas antes del
    módulo de inventario no tienen líneas y conservan solo la descripción y el total.
    """

    class Estado(models.TextChoices):
        VIGENTE = 'VIGENTE', 'Vigente'
        ANULADA = 'ANULADA', 'Anulada'

    fecha = models.DateTimeField(auto_now_add=True)
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ventas',
    )
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='ventas')
    cliente_nombre = models.CharField('cliente', max_length=150)
    cliente_ci = models.CharField('CI/NIT del cliente', max_length=20, blank=True)
    descripcion = models.CharField('observación', max_length=255, blank=True)
    descuento = models.DecimalField('descuento (Bs)', max_digits=10, decimal_places=2, default=Decimal('0'),
                                    validators=[MinValueValidator(Decimal('0'))])
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=MONTO_POSITIVO)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.VIGENTE)
    fecha_anulacion = models.DateTimeField('fecha de anulación', null=True, blank=True)
    usuario_anulacion = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name='ventas_anuladas', verbose_name='anulada por',
    )
    motivo_anulacion = models.CharField('motivo de la anulación', max_length=255, blank=True)

    class Meta:
        verbose_name = 'venta'
        verbose_name_plural = 'ventas'
        ordering = ['-fecha']
        permissions = [
            ('registrar_venta', 'Puede registrar ventas y cobrar pagos'),
            ('ver_todas_ventas', 'Puede ver las ventas de todos los vendedores'),
            ('anular_venta', 'Puede anular ventas'),
        ]

    def __str__(self):
        return f'Nota de venta {self.numero}'

    @property
    def numero(self):
        return f'{self.pk:06d}' if self.pk else '—'

    @property
    def total_pagado(self):
        return self.pagos.aggregate(t=Sum('monto'))['t'] or Decimal('0')

    @property
    def saldo(self):
        return self.total - self.total_pagado

    @property
    def subtotal(self):
        return self.total + self.descuento


class DetalleVenta(models.Model):
    """Línea de la venta. Guarda el precio y el costo del momento, aunque el catálogo cambie después."""

    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    articulo = models.ForeignKey(Articulo, on_delete=models.PROTECT, related_name='+', verbose_name='artículo')
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField('precio unitario (Bs)', max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(
        'costo unitario (Bs)', max_digits=12, decimal_places=4, default=Decimal('0'),
        help_text='Costo promedio al vender. Al anular, el stock vuelve con este costo.',
    )

    class Meta:
        verbose_name = 'detalle de venta'
        verbose_name_plural = 'detalles de venta'
        constraints = [models.UniqueConstraint(fields=['venta', 'articulo'], name='venta_articulo_unico')]

    def __str__(self):
        return f'{self.cantidad} × {self.articulo}'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


class Pago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT, related_name='pagos')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pagos_cobrados',
    )
    movimiento_caja = models.OneToOneField(
        MovimientoCaja, on_delete=models.PROTECT, related_name='pago',
    )
    fecha = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=MONTO_POSITIVO)
    forma_pago = models.CharField('forma de pago', max_length=10, choices=FormaPago.choices)

    class Meta:
        verbose_name = 'pago'
        verbose_name_plural = 'pagos'
        ordering = ['fecha']

    def __str__(self):
        return f'Pago {self.monto} · venta {self.venta.numero}'

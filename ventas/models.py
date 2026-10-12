from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum

from caja.models import MONTO_POSITIVO, FormaPago, MovimientoCaja
from core.models import Sucursal


class Venta(models.Model):
    """Encabezado de la venta (nota de venta).

    El detalle de productos se agregará cuando exista el módulo de inventario;
    por ahora la venta registra una descripción y el total.
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
    descripcion = models.CharField('descripción', max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=MONTO_POSITIVO)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.VIGENTE)

    class Meta:
        verbose_name = 'venta'
        verbose_name_plural = 'ventas'
        ordering = ['-fecha']
        permissions = [
            ('registrar_venta', 'Puede registrar ventas y cobrar pagos'),
            ('ver_todas_ventas', 'Puede ver las ventas de todos los vendedores'),
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

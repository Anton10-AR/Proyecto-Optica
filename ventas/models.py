from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from caja.models import MONTO_POSITIVO, FormaPago, MovimientoCaja
from core.models import Sucursal, validar_telefono
from inventario.models import Articulo


class Cliente(models.Model):
    """Datos básicos del cliente (RF05). Es obligatorio en las ventas de lentes graduados, porque tiene la receta."""

    nombre = models.CharField('nombres y apellidos', max_length=150)
    ci_nit = models.CharField('CI/NIT', max_length=20, unique=True, null=True, blank=True)
    telefono = models.CharField('teléfono', max_length=13, blank=True, validators=[validar_telefono])
    correo = models.EmailField('correo electrónico', blank=True)
    fecha_nacimiento = models.DateField('fecha de nacimiento', null=True, blank=True)
    direccion = models.CharField('dirección', max_length=200, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
        ordering = ['nombre']
        permissions = [('gestionar_clientes', 'Puede registrar y editar clientes')]

    def __str__(self):
        return self.nombre

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy, nacimiento = timezone.localdate(), self.fecha_nacimiento
        return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))


def _multiplo_de_cuarto(valor):
    return valor is None or (valor * 4) == int(valor * 4)


class Receta(models.Model):
    """Receta oftalmológica del cliente (RF21). No se edita: una graduación nueva es una receta nueva (RF22)."""

    class Origen(models.TextChoices):
        EXAMEN = 'EXAMEN', 'Examen en la óptica'
        EXTERNA = 'EXTERNA', 'Receta externa'

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='recetas')
    fecha = models.DateField(default=timezone.localdate, help_text='Fecha del examen o de la receta externa.')
    origen = models.CharField(max_length=10, choices=Origen.choices, default=Origen.EXAMEN)
    optico = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='examenes',
        verbose_name='óptico responsable', help_text='Quién hizo el examen en la óptica.',
    )
    medico = models.CharField('médico o institución', max_length=150, blank=True,
                              help_text='Quién emitió la receta externa.')
    od_esfera = models.DecimalField('OD esfera', max_digits=5, decimal_places=2)
    od_cilindro = models.DecimalField('OD cilindro', max_digits=5, decimal_places=2, default=Decimal('0'))
    od_eje = models.PositiveSmallIntegerField('OD eje', null=True, blank=True)
    od_adicion = models.DecimalField('OD adición', max_digits=4, decimal_places=2, null=True, blank=True)
    oi_esfera = models.DecimalField('OI esfera', max_digits=5, decimal_places=2)
    oi_cilindro = models.DecimalField('OI cilindro', max_digits=5, decimal_places=2, default=Decimal('0'))
    oi_eje = models.PositiveSmallIntegerField('OI eje', null=True, blank=True)
    oi_adicion = models.DecimalField('OI adición', max_digits=4, decimal_places=2, null=True, blank=True)
    distancia_pupilar = models.DecimalField(
        'distancia pupilar (mm)', max_digits=4, decimal_places=1,
        validators=[MinValueValidator(Decimal('40')), MaxValueValidator(Decimal('80'))],
    )
    observaciones = models.CharField(max_length=255, blank=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                       related_name='recetas_registradas')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'receta'
        verbose_name_plural = 'recetas'
        ordering = ['-fecha', '-pk']
        permissions = [
            ('registrar_receta', 'Puede registrar recetas de los clientes'),
            ('realizar_examen', 'Realiza exámenes visuales (figura como óptico responsable)'),
        ]

    def __str__(self):
        return f'Receta del {self.fecha:%d/%m/%Y} · {self.cliente}'

    def clean(self):
        errores = {}
        for ojo in ('od', 'oi'):
            esfera, cilindro = getattr(self, f'{ojo}_esfera'), getattr(self, f'{ojo}_cilindro')
            eje, adicion = getattr(self, f'{ojo}_eje'), getattr(self, f'{ojo}_adicion')
            if esfera is not None and not (-25 <= esfera <= 25 and _multiplo_de_cuarto(esfera)):
                errores[f'{ojo}_esfera'] = 'Entre -25,00 y +25,00, en pasos de 0,25.'
            if cilindro is not None and not (-10 <= cilindro <= 10 and _multiplo_de_cuarto(cilindro)):
                errores[f'{ojo}_cilindro'] = 'Entre -10,00 y +10,00, en pasos de 0,25.'
            if cilindro:
                if eje is None or not 1 <= eje <= 180:
                    errores[f'{ojo}_eje'] = 'Con cilindro, indique el eje (de 1 a 180°).'
            elif eje is not None:
                errores[f'{ojo}_eje'] = 'Sin cilindro, deje el eje vacío.'
            if adicion is not None and not (Decimal('0.25') <= adicion <= 4 and _multiplo_de_cuarto(adicion)):
                errores[f'{ojo}_adicion'] = 'Entre +0,25 y +4,00, en pasos de 0,25.'
        if self.origen == self.Origen.EXAMEN:
            if not self.optico_id:
                errores['optico'] = 'Indique el óptico que hizo el examen.'
            if self.medico.strip():
                errores['medico'] = 'Una receta de examen en la óptica no lleva médico externo.'
        else:
            if not self.medico.strip():
                errores['medico'] = 'Indique el médico o la institución que emitió la receta.'
            if self.optico_id:
                errores['optico'] = 'Una receta externa no lleva óptico responsable.'
        if self.fecha and self.fecha > timezone.localdate():
            errores['fecha'] = 'La fecha no puede ser futura.'
        if errores:
            raise ValidationError(errores)

    @property
    def responsable(self):
        return self.optico if self.origen == self.Origen.EXAMEN else self.medico


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
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, null=True, blank=True, related_name='ventas',
        help_text='Vacío en las ventas a clientes ocasionales.',
    )
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


class OrdenTrabajo(models.Model):
    """Orden para el taller propio, generada al vender lentes graduados (RF23, RF24, RF31)."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_TALLER = 'EN_TALLER', 'En taller'
        LISTO = 'LISTO', 'Listo para entregar'
        ENTREGADO = 'ENTREGADO', 'Entregado'
        ANULADA = 'ANULADA', 'Anulada'

    venta = models.OneToOneField(Venta, on_delete=models.PROTECT, related_name='orden')
    receta = models.ForeignKey(Receta, on_delete=models.PROTECT, related_name='ordenes')
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_prometida = models.DateField('entrega prometida', null=True, blank=True)
    entrega_autorizada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name='entregas_autorizadas', verbose_name='entrega con saldo autorizada por',
    )
    fecha_autorizacion = models.DateTimeField('fecha de la autorización', null=True, blank=True)
    motivo_autorizacion = models.CharField('motivo de la autorización', max_length=255, blank=True)

    class Meta:
        verbose_name = 'orden de trabajo'
        verbose_name_plural = 'órdenes de trabajo'
        ordering = ['-fecha']
        permissions = [
            ('ver_ordenes', 'Puede consultar las órdenes de trabajo'),
            ('actualizar_ordenes', 'Puede pasar las órdenes al taller y marcarlas como listas'),
            ('entregar_ordenes', 'Puede entregar los trabajos al cliente'),
            ('autorizar_entrega_con_saldo', 'Puede autorizar la entrega de un trabajo con saldo pendiente'),
        ]

    def __str__(self):
        return f'Orden de trabajo {self.numero}'

    @property
    def numero(self):
        return f'{self.pk:06d}' if self.pk else '—'

    @property
    def siguiente_estado(self):
        """El taller avanza la orden un paso: pendiente → en taller → listo. La entrega es aparte (RF31)."""
        return {self.Estado.PENDIENTE: self.Estado.EN_TALLER, self.Estado.EN_TALLER: self.Estado.LISTO}.get(self.estado)

    @property
    def activa(self):
        return self.estado in (self.Estado.PENDIENTE, self.Estado.EN_TALLER, self.Estado.LISTO)

    @property
    def entrega_autorizada(self):
        return self.entrega_autorizada_por_id is not None


class EventoOrden(models.Model):
    """Historial de la orden: quién la cambió de estado y cuándo."""

    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='eventos')
    estado = models.CharField(max_length=10, choices=OrdenTrabajo.Estado.choices)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='eventos_orden')
    fecha = models.DateTimeField(auto_now_add=True)
    nota = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'evento de la orden'
        verbose_name_plural = 'eventos de las órdenes'
        ordering = ['fecha', 'pk']

    def __str__(self):
        return f'{self.orden} · {self.get_estado_display()}'

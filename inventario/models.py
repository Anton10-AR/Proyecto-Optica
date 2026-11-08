from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower

from core.models import Sucursal, validar_telefono

MONTO_POSITIVO = [MinValueValidator(Decimal('0.01'))]
CANTIDAD_POSITIVA = [MinValueValidator(1)]


class Categoria(models.Model):
    """Agrupa los artículos: armazones, lunas, lentes de contacto, accesorios, servicios."""

    nombre = models.CharField(max_length=60)
    descripcion = models.CharField('descripción', max_length=200, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(Lower('nombre'), name='categoria_nombre_unico',
                                    violation_error_message='Ya existe una categoría con este nombre.'),
        ]

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    razon_social = models.CharField('razón social', max_length=150)
    nit = models.CharField('NIT', max_length=20, unique=True, null=True, blank=True)
    contacto = models.CharField('persona de contacto', max_length=100, blank=True)
    telefono = models.CharField('teléfono', max_length=13, blank=True, validators=[validar_telefono])
    correo = models.EmailField('correo electrónico', blank=True)
    direccion = models.CharField('dirección', max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'proveedor'
        verbose_name_plural = 'proveedores'
        ordering = ['razon_social']
        permissions = [('gestionar_proveedores', 'Puede ver, crear y editar proveedores')]
        constraints = [
            models.UniqueConstraint(Lower('razon_social'), name='proveedor_razon_social_unica',
                                    violation_error_message='Ya existe un proveedor con esta razón social.'),
        ]

    def __str__(self):
        return self.razon_social


class Articulo(models.Model):
    """Artículo del catálogo. Las existencias se llevan por sucursal en `Existencia`.

    Las lunas se registran por tipo (material, diseño y tratamiento), no por graduación:
    la graduación es de la receta y de la orden de trabajo. Los servicios (examen visual,
    montaje) no controlan stock.
    """

    codigo = models.CharField('código', max_length=30, unique=True)
    codigo_barras = models.CharField('código de barras', max_length=50, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='articulos',
                                  verbose_name='categoría')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, null=True, blank=True,
                                  related_name='articulos', help_text='Proveedor habitual (opcional).')
    marca = models.CharField(max_length=60, blank=True)
    precio_venta = models.DecimalField('precio de venta (Bs)', max_digits=10, decimal_places=2,
                                       validators=MONTO_POSITIVO)
    costo_promedio = models.DecimalField(
        'costo promedio (Bs)', max_digits=12, decimal_places=4, default=Decimal('0'), editable=False,
        help_text='Lo recalcula cada ingreso de mercadería (promedio ponderado).',
    )
    stock_minimo = models.PositiveIntegerField(
        'stock mínimo', default=0, help_text='Cantidad por sucursal a partir de la cual se genera una alerta.',
    )
    controla_stock = models.BooleanField(
        'controla stock', default=True,
        help_text='Desmárquelo para los servicios (examen visual, montaje), que no tienen existencias.',
    )
    requiere_receta = models.BooleanField(
        'lente graduado', default=False,
        help_text='Márquelo en las lunas que se tallan según la receta: su venta exige una receta del cliente, '
                  'un anticipo mínimo y genera una orden de trabajo para el taller.',
    )
    activo = models.BooleanField(default=True, help_text='Un artículo inactivo no se puede vender ni ingresar.')

    class Meta:
        verbose_name = 'artículo'
        verbose_name_plural = 'artículos'
        ordering = ['nombre']
        permissions = [
            ('ver_articulos', 'Puede consultar los artículos, sus precios y su stock'),
            ('gestionar_catalogo', 'Puede crear y editar artículos y categorías'),
            ('ver_kardex', 'Puede ver el kardex y los costos de los artículos'),
        ]

    def __str__(self):
        return f'{self.codigo} · {self.nombre}'


class Existencia(models.Model):
    """Stock de un artículo en una sucursal.

    Solo la modifican las funciones de `inventario.servicios`, que además registran el
    kardex en la misma transacción (RNF05). La cantidad no puede ser negativa.
    """

    articulo = models.ForeignKey(Articulo, on_delete=models.PROTECT, related_name='existencias',
                                 verbose_name='artículo')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='existencias')
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'existencia'
        verbose_name_plural = 'existencias'
        constraints = [
            models.UniqueConstraint(fields=['articulo', 'sucursal'], name='existencia_unica_por_sucursal'),
            models.CheckConstraint(condition=models.Q(cantidad__gte=0), name='existencia_no_negativa'),
        ]

    def __str__(self):
        return f'{self.articulo} en {self.sucursal}: {self.cantidad}'


class Ingreso(models.Model):
    """Ingreso de mercadería por compra a un proveedor (RF09). Cada línea es una entrada del kardex."""

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='ingresos')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='ingresos')
    documento = models.CharField(
        'factura o nota del proveedor', max_length=40, blank=True,
        help_text='Número del comprobante de compra, si lo hay.',
    )
    observacion = models.CharField('observación', max_length=255, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ingresos')

    class Meta:
        verbose_name = 'ingreso de mercadería'
        verbose_name_plural = 'ingresos de mercadería'
        ordering = ['-fecha']
        permissions = [('registrar_ingresos', 'Puede registrar ingresos de mercadería por compra')]

    @property
    def numero(self):
        return f'{self.pk:06d}' if self.pk else '—'

    @property
    def total(self):
        return sum((d.subtotal for d in self.detalles.all()), Decimal('0'))

    def __str__(self):
        return f'Ingreso {self.numero}'


class DetalleIngreso(models.Model):
    ingreso = models.ForeignKey(Ingreso, on_delete=models.CASCADE, related_name='detalles')
    articulo = models.ForeignKey(Articulo, on_delete=models.PROTECT, related_name='+', verbose_name='artículo')
    cantidad = models.PositiveIntegerField(validators=CANTIDAD_POSITIVA)
    costo_unitario = models.DecimalField('costo unitario (Bs)', max_digits=12, decimal_places=4,
                                         validators=MONTO_POSITIVO)

    class Meta:
        verbose_name = 'línea de ingreso'
        verbose_name_plural = 'líneas de ingreso'

    @property
    def subtotal(self):
        return self.cantidad * self.costo_unitario


class Ajuste(models.Model):
    """Baja (rotura, pérdida, vencimiento) o ajuste por conteo físico de un artículo en una sucursal."""

    class Tipo(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        AJUSTE_ENTRADA = 'AJUSTE_ENTRADA', 'Ajuste de entrada (sobrante)'
        AJUSTE_SALIDA = 'AJUSTE_SALIDA', 'Ajuste de salida (faltante)'

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='ajustes')
    articulo = models.ForeignKey(Articulo, on_delete=models.PROTECT, related_name='ajustes', verbose_name='artículo')
    tipo = models.CharField(max_length=15, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField(validators=CANTIDAD_POSITIVA)
    motivo = models.CharField(max_length=255, help_text='Por qué se da de baja o se ajusta (obligatorio).')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ajustes')

    class Meta:
        verbose_name = 'baja o ajuste'
        verbose_name_plural = 'bajas y ajustes'
        ordering = ['-fecha']
        permissions = [('registrar_ajustes', 'Puede registrar bajas y ajustes de inventario')]

    @property
    def numero(self):
        return f'{self.pk:06d}' if self.pk else '—'

    @property
    def es_entrada(self):
        return self.tipo == self.Tipo.AJUSTE_ENTRADA

    def __str__(self):
        return f'{self.get_tipo_display()} {self.numero}'


class Traspaso(models.Model):
    """Traspaso entre sucursales en dos pasos (RF10).

    Al enviarlo, la mercadería sale del stock del origen; al recibirlo, entra al del destino.
    Mientras está enviado, no está disponible en ninguna de las dos sucursales.
    """

    class Estado(models.TextChoices):
        ENVIADO = 'ENVIADO', 'Enviado'
        RECIBIDO = 'RECIBIDO', 'Recibido'

    origen = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='traspasos_enviados')
    destino = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='traspasos_recibidos')
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ENVIADO)
    observacion = models.CharField('observación', max_length=255, blank=True)
    fecha_envio = models.DateTimeField('fecha de envío', auto_now_add=True, db_index=True)
    usuario_envio = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                      related_name='traspasos_enviados', verbose_name='enviado por')
    fecha_recepcion = models.DateTimeField('fecha de recepción', null=True, blank=True)
    usuario_recepcion = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
                                          related_name='traspasos_recibidos', verbose_name='recibido por')

    class Meta:
        verbose_name = 'traspaso'
        verbose_name_plural = 'traspasos'
        ordering = ['-fecha_envio']
        permissions = [
            ('enviar_traspasos', 'Puede enviar mercadería a otra sucursal'),
            ('recibir_traspasos', 'Puede recibir los traspasos dirigidos a su sucursal'),
        ]
        constraints = [
            models.CheckConstraint(condition=~models.Q(origen=models.F('destino')),
                                   name='traspaso_entre_sucursales_distintas'),
        ]

    @property
    def numero(self):
        return f'{self.pk:06d}' if self.pk else '—'

    def __str__(self):
        return f'Traspaso {self.numero}'


class DetalleTraspaso(models.Model):
    traspaso = models.ForeignKey(Traspaso, on_delete=models.CASCADE, related_name='detalles')
    articulo = models.ForeignKey(Articulo, on_delete=models.PROTECT, related_name='+', verbose_name='artículo')
    cantidad = models.PositiveIntegerField(validators=CANTIDAD_POSITIVA)

    class Meta:
        verbose_name = 'línea de traspaso'
        verbose_name_plural = 'líneas de traspaso'


class Movimiento(models.Model):
    """Una línea del kardex (RF11): entrada o salida de un artículo en una sucursal.

    Guarda el saldo de la sucursal y el costo promedio del artículo después del movimiento.
    Nunca se edita ni se borra: lo crean solo las funciones de `inventario.servicios`.
    """

    class Tipo(models.TextChoices):
        COMPRA = 'COMPRA', 'Ingreso por compra'
        VENTA = 'VENTA', 'Salida por venta'
        ANULACION_VENTA = 'ANULACION_VENTA', 'Reposición por venta anulada'
        BAJA = 'BAJA', 'Baja'
        AJUSTE_ENTRADA = 'AJUSTE_ENTRADA', 'Ajuste de entrada'
        AJUSTE_SALIDA = 'AJUSTE_SALIDA', 'Ajuste de salida'
        TRASPASO_SALIDA = 'TRASPASO_SALIDA', 'Traspaso enviado'
        TRASPASO_ENTRADA = 'TRASPASO_ENTRADA', 'Traspaso recibido'

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    articulo = models.ForeignKey(Articulo, on_delete=models.PROTECT, related_name='movimientos',
                                 verbose_name='artículo')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='movimientos_inventario')
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField(validators=CANTIDAD_POSITIVA)
    costo_unitario = models.DecimalField('costo unitario (Bs)', max_digits=12, decimal_places=4)
    saldo = models.PositiveIntegerField(help_text='Existencias de la sucursal después del movimiento.')
    costo_promedio = models.DecimalField('costo promedio (Bs)', max_digits=12, decimal_places=4,
                                         help_text='Costo promedio del artículo después del movimiento.')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                related_name='movimientos_inventario')
    referencia = models.CharField(max_length=60, help_text='Documento de origen, por ejemplo "Ingreso 000012".')
    ingreso = models.ForeignKey(Ingreso, on_delete=models.PROTECT, null=True, blank=True, related_name='movimientos')
    ajuste = models.ForeignKey(Ajuste, on_delete=models.PROTECT, null=True, blank=True, related_name='movimientos')
    traspaso = models.ForeignKey(Traspaso, on_delete=models.PROTECT, null=True, blank=True,
                                 related_name='movimientos')

    class Meta:
        verbose_name = 'movimiento de inventario'
        verbose_name_plural = 'movimientos de inventario (kardex)'
        ordering = ['fecha', 'pk']
        indexes = [models.Index(fields=['articulo', 'sucursal', 'fecha'])]

    @property
    def es_entrada(self):
        return self.tipo in ENTRADAS

    @property
    def valor(self):
        """Valor del movimiento al costo con que se registró."""
        return self.cantidad * self.costo_unitario

    @property
    def saldo_valorado(self):
        return self.saldo * self.costo_promedio

    def __str__(self):
        return f'{self.get_tipo_display()} · {self.articulo.codigo} · {self.cantidad}'


ENTRADAS = {Movimiento.Tipo.COMPRA, Movimiento.Tipo.ANULACION_VENTA, Movimiento.Tipo.AJUSTE_ENTRADA,
            Movimiento.Tipo.TRASPASO_ENTRADA}

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower

from core.models import Sucursal, validar_telefono


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
                                       validators=[MinValueValidator(Decimal('0.01'))])
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
    activo = models.BooleanField(default=True, help_text='Un artículo inactivo no se puede vender ni ingresar.')

    class Meta:
        verbose_name = 'artículo'
        verbose_name_plural = 'artículos'
        ordering = ['nombre']
        permissions = [
            ('ver_articulos', 'Puede consultar los artículos, sus precios y su stock'),
            ('gestionar_catalogo', 'Puede crear y editar artículos y categorías'),
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

from django import forms

from core.forms import BootstrapMixin

from .models import Articulo, Categoria, Proveedor


def _sin_duplicado(modelo, instancia, campo, valor, mensaje):
    """Rechaza el valor si otro registro ya lo tiene, sin distinguir mayúsculas."""
    if valor and modelo.objects.filter(**{f'{campo}__iexact': valor}).exclude(pk=instancia.pk).exists():
        raise forms.ValidationError(mensaje)
    return valor


class CategoriaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activa']

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        return _sin_duplicado(Categoria, self.instance, 'nombre', nombre, 'Ya existe una categoría con este nombre.')


class ProveedorForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['razon_social', 'nit', 'contacto', 'telefono', 'correo', 'direccion', 'activo']

    def clean_razon_social(self):
        razon = self.cleaned_data['razon_social'].strip()
        return _sin_duplicado(Proveedor, self.instance, 'razon_social', razon,
                              'Ya existe un proveedor con esta razón social.')

    def clean_nit(self):
        # Vacío se guarda como NULL para que varios proveedores puedan no tener NIT.
        nit = (self.cleaned_data['nit'] or '').strip().upper() or None
        return _sin_duplicado(Proveedor, self.instance, 'nit', nit, 'Ya existe un proveedor con este NIT.')

    def clean_correo(self):
        return self.cleaned_data['correo'].strip().lower()


class ArticuloForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ['codigo', 'codigo_barras', 'nombre', 'categoria', 'marca', 'proveedor',
                  'precio_venta', 'stock_minimo', 'controla_stock', 'activo']
        help_texts = {
            'codigo': 'Código interno, por ejemplo ARM-001. Se guarda en mayúsculas.',
            'codigo_barras': 'Opcional. Puede escanearlo con el lector.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se ofrecen solo las opciones activas, más la que ya tenga el artículo.
        categoria, proveedor = self.instance.categoria_id, self.instance.proveedor_id
        self.fields['categoria'].queryset = Categoria.objects.filter(activa=True) | Categoria.objects.filter(pk=categoria)
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True) | Proveedor.objects.filter(pk=proveedor)
        self.fields['categoria'].empty_label = 'Seleccione una categoría'
        self.fields['proveedor'].empty_label = 'Sin proveedor habitual'

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo'].strip().upper()
        return _sin_duplicado(Articulo, self.instance, 'codigo', codigo, 'Ya existe un artículo con este código.')

    def clean_codigo_barras(self):
        codigo = (self.cleaned_data['codigo_barras'] or '').strip() or None
        return _sin_duplicado(Articulo, self.instance, 'codigo_barras', codigo,
                              'Ya existe un artículo con este código de barras.')

    def clean_nombre(self):
        return self.cleaned_data['nombre'].strip()

    def clean_controla_stock(self):
        controla = self.cleaned_data['controla_stock']
        if not controla and self.instance.pk and self.instance.existencias.filter(cantidad__gt=0).exists():
            raise forms.ValidationError('El artículo tiene existencias. Deles de baja antes de dejar de controlar su stock.')
        return controla

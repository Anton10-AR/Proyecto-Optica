from decimal import Decimal

from django import forms

from core.forms import BootstrapMixin
from core.models import Sucursal

from .models import Ajuste, Articulo, Categoria, Proveedor


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


# ---------- Movimientos ----------

def _articulos_con_stock(solo_activos=False):
    articulos = Articulo.objects.filter(controla_stock=True).select_related('categoria')
    return articulos.filter(activo=True) if solo_activos else articulos


class ArticuloChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, articulo):
        return f'{articulo.codigo} · {articulo.nombre}'


class SucursalesMixin:
    """Ofrece solo sucursales activas y propone la del usuario."""

    campos_sucursal = ()

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre in self.campos_sucursal:
            self.fields[nombre].queryset = Sucursal.objects.filter(activa=True)
        if usuario and usuario.sucursal_id and self.campos_sucursal:
            self.fields[self.campos_sucursal[0]].initial = usuario.sucursal_id


class IngresoForm(SucursalesMixin, BootstrapMixin, forms.Form):
    campos_sucursal = ('sucursal',)
    sucursal = forms.ModelChoiceField(label='Sucursal que recibe', queryset=Sucursal.objects.none())
    proveedor = forms.ModelChoiceField(label='Proveedor', queryset=Proveedor.objects.filter(activo=True),
                                       empty_label='Seleccione un proveedor')
    documento = forms.CharField(label='Factura o nota del proveedor', max_length=40, required=False)
    observacion = forms.CharField(label='Observación', max_length=255, required=False)


class LineaIngresoForm(BootstrapMixin, forms.Form):
    articulo = ArticuloChoiceField(label='Artículo', queryset=_articulos_con_stock(solo_activos=True),
                                   empty_label='Seleccione un artículo')
    cantidad = forms.IntegerField(label='Cantidad', min_value=1)
    costo_unitario = forms.DecimalField(label='Costo unitario (Bs)', min_value=Decimal('0.01'), decimal_places=4,
                                        max_digits=12)


class LineaTraspasoForm(BootstrapMixin, forms.Form):
    articulo = ArticuloChoiceField(label='Artículo', queryset=_articulos_con_stock(),
                                   empty_label='Seleccione un artículo')
    cantidad = forms.IntegerField(label='Cantidad', min_value=1)


class LineasFormSet(forms.BaseFormSet):
    """Exige al menos una línea y no permite repetir un artículo."""

    def clean(self):
        if any(self.errors):
            return
        articulos = [f.cleaned_data['articulo'] for f in self.forms if f.cleaned_data]
        if not articulos:
            raise forms.ValidationError('Agregue al menos un artículo.')
        repetidos = {a for a in articulos if articulos.count(a) > 1}
        if repetidos:
            raise forms.ValidationError(
                'Hay artículos repetidos: ' + ', '.join(a.codigo for a in repetidos) + '. Sume las cantidades en una sola línea.')

    def lineas(self, *campos):
        return [tuple(f.cleaned_data[c] for c in ('articulo',) + campos) for f in self.forms if f.cleaned_data]


LineasIngresoFormSet = forms.formset_factory(LineaIngresoForm, formset=LineasFormSet, extra=5)
LineasTraspasoFormSet = forms.formset_factory(LineaTraspasoForm, formset=LineasFormSet, extra=5)


class AjusteForm(SucursalesMixin, BootstrapMixin, forms.Form):
    campos_sucursal = ('sucursal',)
    sucursal = forms.ModelChoiceField(label='Sucursal', queryset=Sucursal.objects.none())
    articulo = ArticuloChoiceField(label='Artículo', queryset=_articulos_con_stock(),
                                   empty_label='Seleccione un artículo')
    tipo = forms.ChoiceField(label='Tipo', choices=Ajuste.Tipo.choices)
    cantidad = forms.IntegerField(label='Cantidad', min_value=1)
    motivo = forms.CharField(label='Motivo', max_length=255,
                             help_text='Por ejemplo: "Armazón roto al exhibirlo" o "Conteo físico del 07/11".')

    def clean_motivo(self):
        return self.cleaned_data['motivo'].strip()


class TraspasoForm(SucursalesMixin, BootstrapMixin, forms.Form):
    campos_sucursal = ('origen', 'destino')
    origen = forms.ModelChoiceField(label='Sucursal de origen', queryset=Sucursal.objects.none())
    destino = forms.ModelChoiceField(label='Sucursal de destino', queryset=Sucursal.objects.none(),
                                     empty_label='Seleccione el destino')
    observacion = forms.CharField(label='Observación', max_length=255, required=False)

    def clean(self):
        datos = super().clean()
        if datos.get('origen') and datos.get('origen') == datos.get('destino'):
            self.add_error('destino', 'El destino debe ser una sucursal distinta del origen.')
        return datos

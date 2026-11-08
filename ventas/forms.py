from decimal import Decimal

from django import forms
from django.db.models import Q, Sum
from django.utils.formats import number_format

from caja.models import FormaPago
from core.forms import BootstrapMixin
from inventario.forms import ArticuloChoiceField, LineasFormSet
from inventario.models import Articulo


class VentaForm(BootstrapMixin, forms.Form):
    cliente_nombre = forms.CharField(label='Cliente', max_length=150)
    cliente_ci = forms.CharField(label='CI/NIT del cliente', max_length=20, required=False)
    descuento = forms.DecimalField(label='Descuento (Bs)', min_value=Decimal('0'), decimal_places=2,
                                   required=False, initial=Decimal('0'),
                                   help_text='Descuento sobre el total, en bolivianos.')
    monto_pago = forms.DecimalField(label='Pago ahora (Bs)', min_value=Decimal('0.01'), decimal_places=2,
                                    help_text='Total o anticipo.')
    forma_pago = forms.ChoiceField(label='Forma de pago', choices=FormaPago.choices)
    observacion = forms.CharField(label='Observación', max_length=255, required=False)

    def clean_descuento(self):
        return self.cleaned_data['descuento'] or Decimal('0')


class ArticuloVentaField(ArticuloChoiceField):
    """Muestra el precio y, si controla stock, las unidades de la sucursal del vendedor."""

    def label_from_instance(self, articulo):
        texto = f'{articulo.codigo} · {articulo.nombre} · Bs {number_format(articulo.precio_venta, 2)}'
        if articulo.controla_stock:
            texto += f' · stock {articulo.stock_sucursal or 0}'
        return texto


class LineaVentaForm(BootstrapMixin, forms.Form):
    articulo = ArticuloVentaField(label='Artículo', queryset=Articulo.objects.none(),
                                  empty_label='Seleccione un artículo')
    cantidad = forms.IntegerField(label='Cantidad', min_value=1)

    def __init__(self, *args, sucursal=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['articulo'].queryset = Articulo.objects.filter(activo=True).annotate(
            stock_sucursal=Sum('existencias__cantidad', filter=Q(existencias__sucursal=sucursal)),
        ).order_by('nombre')


LineasVentaFormSet = forms.formset_factory(LineaVentaForm, formset=LineasFormSet, extra=5)


class PagoForm(BootstrapMixin, forms.Form):
    monto = forms.DecimalField(label='Monto (Bs)', min_value=Decimal('0.01'), decimal_places=2)
    forma_pago = forms.ChoiceField(label='Forma de pago', choices=FormaPago.choices)


class AnularForm(BootstrapMixin, forms.Form):
    motivo = forms.CharField(label='Motivo de la anulación', max_length=255,
                             help_text='Por ejemplo: "El cliente desistió de la compra".')

    def clean_motivo(self):
        return self.cleaned_data['motivo'].strip()

from decimal import Decimal

from django import forms

from caja.models import FormaPago
from core.forms import BootstrapMixin


class VentaForm(BootstrapMixin, forms.Form):
    cliente_nombre = forms.CharField(label='Cliente', max_length=150)
    cliente_ci = forms.CharField(label='CI/NIT del cliente', max_length=20, required=False)
    descripcion = forms.CharField(label='Descripción', max_length=255,
                                  help_text='Productos o servicio vendidos.')
    total = forms.DecimalField(label='Total (Bs)', min_value=Decimal('0.01'), decimal_places=2)
    monto_pago = forms.DecimalField(label='Pago ahora (Bs)', min_value=Decimal('0.01'), decimal_places=2,
                                    help_text='Total o anticipo.')
    forma_pago = forms.ChoiceField(label='Forma de pago', choices=FormaPago.choices)

    def clean(self):
        datos = super().clean()
        total, pago = datos.get('total'), datos.get('monto_pago')
        if total and pago and pago > total:
            self.add_error('monto_pago', 'El pago no puede superar el total.')
        return datos


class PagoForm(BootstrapMixin, forms.Form):
    monto = forms.DecimalField(label='Monto (Bs)', min_value=Decimal('0.01'), decimal_places=2)
    forma_pago = forms.ChoiceField(label='Forma de pago', choices=FormaPago.choices)

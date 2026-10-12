from decimal import Decimal

from django import forms

from core.forms import BootstrapMixin

from .models import FormaPago, MovimientoCaja


class AbrirCajaForm(BootstrapMixin, forms.Form):
    monto_inicial = forms.DecimalField(label='Monto inicial (Bs)', min_value=Decimal('0'), decimal_places=2)
    observacion = forms.CharField(label='Observación', max_length=255, required=False)


class MovimientoForm(BootstrapMixin, forms.Form):
    tipo = forms.ChoiceField(choices=MovimientoCaja.Tipo.choices)
    forma_pago = forms.ChoiceField(label='Forma de pago', choices=FormaPago.choices)
    monto = forms.DecimalField(label='Monto (Bs)', min_value=Decimal('0.01'), decimal_places=2)
    concepto = forms.CharField(max_length=200)


class CerrarCajaForm(BootstrapMixin, forms.Form):
    monto_contado = forms.DecimalField(
        label='Efectivo contado (Bs)', min_value=Decimal('0'), decimal_places=2,
        help_text='Cuente el efectivo de la caja e ingrese el total.',
    )
    observacion = forms.CharField(label='Observación', max_length=255, required=False)

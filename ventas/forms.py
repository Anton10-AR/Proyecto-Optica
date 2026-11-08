from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.utils.formats import number_format

from caja.models import FormaPago
from core.forms import BootstrapMixin
from inventario.forms import ArticuloChoiceField, LineasFormSet
from inventario.models import Articulo

from .models import Cliente, Receta

FECHA = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')


# ---------- Clientes y recetas ----------

class ClienteForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'ci_nit', 'telefono', 'correo', 'fecha_nacimiento', 'direccion']
        widgets = {'fecha_nacimiento': FECHA}
        help_texts = {'ci_nit': 'Opcional, pero no puede repetirse entre clientes.'}

    def clean_nombre(self):
        return ' '.join(self.cleaned_data['nombre'].split())

    def clean_ci_nit(self):
        ci = (self.cleaned_data.get('ci_nit') or '').strip().upper()
        if not ci:
            return None
        if Cliente.objects.filter(ci_nit__iexact=ci).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya hay un cliente con este CI/NIT.')
        return ci


def opticos():
    """Usuarios activos que realizan exámenes visuales (permiso ventas.realizar_examen por su rol)."""
    return get_user_model().objects.filter(
        is_active=True, groups__permissions__codename='realizar_examen',
        groups__permissions__content_type__app_label='ventas',
    ).distinct().order_by('first_name', 'last_name')


class OpticoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, usuario):
        return usuario.get_full_name() or usuario.username


GRADUACION = {'step': '0.25'}


class RecetaForm(BootstrapMixin, forms.ModelForm):
    optico = OpticoChoiceField(label='Óptico responsable', queryset=None, required=False,
                               empty_label='Seleccione el óptico')

    class Meta:
        model = Receta
        fields = ['fecha', 'origen', 'optico', 'medico',
                  'od_esfera', 'od_cilindro', 'od_eje', 'od_adicion',
                  'oi_esfera', 'oi_cilindro', 'oi_eje', 'oi_adicion',
                  'distancia_pupilar', 'observaciones']
        widgets = {
            'fecha': FECHA,
            'od_esfera': forms.NumberInput(attrs=GRADUACION), 'oi_esfera': forms.NumberInput(attrs=GRADUACION),
            'od_cilindro': forms.NumberInput(attrs=GRADUACION), 'oi_cilindro': forms.NumberInput(attrs=GRADUACION),
            'od_adicion': forms.NumberInput(attrs=GRADUACION), 'oi_adicion': forms.NumberInput(attrs=GRADUACION),
            'od_eje': forms.NumberInput(attrs={'min': 1, 'max': 180}),
            'oi_eje': forms.NumberInput(attrs={'min': 1, 'max': 180}),
            'distancia_pupilar': forms.NumberInput(attrs={'step': '0.5'}),
        }
        labels = {f'{ojo}_{campo}': nombre for ojo in ('od', 'oi') for campo, nombre in
                  (('esfera', 'Esfera'), ('cilindro', 'Cilindro'), ('eje', 'Eje (°)'), ('adicion', 'Adición'))}

    def __init__(self, *args, cliente=None, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.cliente = cliente
        self.instance.registrado_por = usuario
        self.fields['optico'].queryset = opticos()
        if usuario is not None and self.fields['optico'].queryset.filter(pk=usuario.pk).exists():
            self.fields['optico'].initial = usuario.pk
        self.fields['medico'].widget.attrs['placeholder'] = 'Por ejemplo: Dr. Mario Salinas, Clínica Los Andes'

    def clean(self):
        datos = super().clean()
        # La pantalla oculta el campo que no corresponde al origen, pero su valor igual se envía: se descarta.
        if datos.get('origen') == Receta.Origen.EXTERNA:
            datos['optico'] = None
        elif datos.get('origen') == Receta.Origen.EXAMEN:
            datos['medico'] = ''
        return datos


# ---------- Venta ----------

class RecetaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, receta):
        return f'{receta.fecha:%d/%m/%Y} · {receta.get_origen_display()} · {receta.responsable or ""}'


class VentaForm(BootstrapMixin, forms.Form):
    cliente = forms.ModelChoiceField(
        label='Cliente registrado', queryset=Cliente.objects.order_by('nombre'), required=False,
        empty_label='Cliente ocasional (sin registrar)',
        help_text='Obligatorio si la venta incluye lentes graduados.',
    )
    cliente_nombre = forms.CharField(label='Nombre del cliente ocasional', max_length=150, required=False)
    cliente_ci = forms.CharField(label='CI/NIT del cliente ocasional', max_length=20, required=False)
    receta = RecetaChoiceField(label='Receta para el taller', queryset=Receta.objects.none(), required=False,
                               empty_label='—', help_text='Solo para lentes graduados.')
    fecha_prometida = forms.DateField(label='Entrega prometida', required=False, widget=FECHA,
                                      help_text='Para la orden de trabajo.')
    descuento = forms.DecimalField(label='Descuento (Bs)', min_value=Decimal('0'), decimal_places=2,
                                   required=False, initial=Decimal('0'),
                                   help_text='Descuento sobre el total, en bolivianos.')
    monto_pago = forms.DecimalField(label='Pago ahora (Bs)', min_value=Decimal('0.01'), decimal_places=2,
                                    help_text='Total o anticipo.')
    forma_pago = forms.ChoiceField(label='Forma de pago', choices=FormaPago.choices)
    observacion = forms.CharField(label='Observación', max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Las recetas que se ofrecen son las del cliente elegido; al cambiarlo, HTMX recarga la lista.
        cliente = self.data.get('cliente') if self.is_bound else self.initial.get('cliente')
        cliente = getattr(cliente, 'pk', cliente)
        if str(cliente or '').isdigit():
            self.fields['receta'].queryset = Receta.objects.filter(cliente_id=cliente)
        self.fields['cliente'].widget.attrs.update({
            'hx-get': reverse_lazy('venta_recetas'), 'hx-target': '#id_receta', 'hx-trigger': 'change',
        })

    def clean_descuento(self):
        return self.cleaned_data['descuento'] or Decimal('0')

    def clean(self):
        datos = super().clean()
        if not datos.get('cliente') and not (datos.get('cliente_nombre') or '').strip() and 'cliente' not in self.errors:
            self.add_error('cliente_nombre', 'Elija un cliente registrado o escriba el nombre del cliente ocasional.')
        return datos


class ArticuloVentaField(ArticuloChoiceField):
    """Muestra el precio y, si controla stock, las unidades de la sucursal del vendedor."""

    def label_from_instance(self, articulo):
        texto = f'{articulo.codigo} · {articulo.nombre} · Bs {number_format(articulo.precio_venta, 2)}'
        if articulo.controla_stock:
            texto += f' · stock {articulo.stock_sucursal or 0}'
        if articulo.requiere_receta:
            texto += ' · con receta'
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


class MotivoForm(BootstrapMixin, forms.Form):
    motivo = forms.CharField(label='Motivo', max_length=255)

    def clean_motivo(self):
        return self.cleaned_data['motivo'].strip()


class AnularForm(MotivoForm):
    motivo = forms.CharField(label='Motivo de la anulación', max_length=255,
                             help_text='Por ejemplo: "El cliente desistió de la compra".')


class AutorizarEntregaForm(MotivoForm):
    motivo = forms.CharField(label='Motivo de la autorización', max_length=255,
                             help_text='Por ejemplo: "Cliente frecuente; paga el saldo el viernes".')

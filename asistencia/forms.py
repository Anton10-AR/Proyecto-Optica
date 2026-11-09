from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.functions import Lower
from django.utils import timezone

from core.forms import BootstrapMixin
from core.models import Sucursal

from .models import DIAS_SEMANA, AsignacionHorario, Ausencia, Feriado, Horario, TramoHorario

FECHA = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
HORA = forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
TRAMOS_POR_DIA = 2  # la pantalla admite dos tramos por día (horario partido); el modelo admite más


class MarcacionForm(forms.Form):
    latitud = forms.DecimalField(min_value=-90, max_value=90)
    longitud = forms.DecimalField(min_value=-180, max_value=180)


class EmpleadoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, usuario):
        return f'{usuario.get_full_name() or usuario.username} · {usuario.sucursal or "sin sucursal"}'


# ---------- Horarios (RF17) ----------

class HorarioForm(BootstrapMixin, forms.ModelForm):
    """Horario con una grilla de días × tramos. Cada tramo es una hora de entrada y una de salida."""

    class Meta:
        model = Horario
        fields = ['nombre', 'descripcion', 'activo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existentes = self.instance.tramos_por_dia() if self.instance.pk else {}
        for dia, _ in DIAS_SEMANA:
            for n in range(1, TRAMOS_POR_DIA + 1):
                tramo = existentes.get(dia, [])[n - 1] if len(existentes.get(dia, [])) >= n else None
                for campo, hora in (('e', 'hora_entrada'), ('s', 'hora_salida')):
                    self.fields[f'd{dia}_{campo}{n}'] = forms.TimeField(
                        required=False, widget=HORA, initial=getattr(tramo, hora, None),
                        label=f'{"Entrada" if campo == "e" else "Salida"} {n}')
        for nombre in self.fields:
            if nombre.startswith('d') and '_' in nombre:
                self.fields[nombre].widget.attrs.update({'class': 'form-control form-control-sm'})

    def clean_nombre(self):
        nombre = ' '.join(self.cleaned_data['nombre'].split())
        repetido = Horario.objects.annotate(n=Lower('nombre')).filter(n=nombre.lower()).exclude(pk=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError('Ya existe un horario con este nombre.')
        return nombre

    def filas(self):
        """[(nombre del día, [(campo entrada, campo salida), ...]), ...] para dibujar la grilla."""
        return [(nombre, [(self[f'd{dia}_e{n}'], self[f'd{dia}_s{n}']) for n in range(1, TRAMOS_POR_DIA + 1)])
                for dia, nombre in DIAS_SEMANA]

    def tramos(self):
        """[(día, entrada, salida), ...] a partir de los datos validados."""
        datos = self.cleaned_data
        return [(dia, datos[f'd{dia}_e{n}'], datos[f'd{dia}_s{n}']) for dia, _ in DIAS_SEMANA
                for n in range(1, TRAMOS_POR_DIA + 1) if datos.get(f'd{dia}_e{n}')]

    def clean(self):
        datos = super().clean()
        hay_tramos = False
        for dia, nombre in DIAS_SEMANA:
            salida_anterior = None
            for n in range(1, TRAMOS_POR_DIA + 1):
                entrada, salida = datos.get(f'd{dia}_e{n}'), datos.get(f'd{dia}_s{n}')
                if f'd{dia}_e{n}' in self.errors or f'd{dia}_s{n}' in self.errors:
                    continue
                if bool(entrada) != bool(salida):
                    self.add_error(f'd{dia}_e{n}', f'{nombre}: indique la entrada y la salida del tramo {n}.')
                    continue
                if not entrada:
                    continue
                if n > 1 and not datos.get(f'd{dia}_e{n - 1}'):
                    self.add_error(f'd{dia}_e{n}', f'{nombre}: complete primero el tramo {n - 1}.')
                elif entrada >= salida:
                    self.add_error(f'd{dia}_e{n}', f'{nombre}: la entrada del tramo {n} debe ser antes de la salida.')
                elif salida_anterior and entrada <= salida_anterior:
                    self.add_error(f'd{dia}_e{n}', f'{nombre}: el tramo {n} debe empezar después del tramo {n - 1}.')
                hay_tramos = True
                salida_anterior = salida
        if not hay_tramos and not self.errors:
            raise forms.ValidationError('Indique al menos un tramo en la semana.')
        return datos

    @transaction.atomic
    def save(self, commit=True):
        horario = super().save()
        horario.tramos.all().delete()
        TramoHorario.objects.bulk_create([
            TramoHorario(horario=horario, dia_semana=dia, hora_entrada=entrada, hora_salida=salida)
            for dia, entrada, salida in self.tramos()
        ])
        return horario


class AsignacionForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = AsignacionHorario
        fields = ['horario', 'desde']
        widgets = {'desde': FECHA}
        help_texts = {'desde': 'Los días anteriores se siguen calculando con el horario que tenían.'}

    def __init__(self, *args, usuario=None, registrado_por=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.usuario = usuario
        self.instance.registrado_por = registrado_por
        self.fields['horario'].queryset = Horario.objects.filter(activo=True)
        self.fields['horario'].empty_label = 'Seleccione un horario'
        self.fields['desde'].initial = timezone.localdate()

    def clean_desde(self):
        desde = self.cleaned_data['desde']
        if AsignacionHorario.objects.filter(usuario=self.instance.usuario, desde=desde).exists():
            raise forms.ValidationError('El empleado ya tiene un horario asignado desde esa fecha.')
        return desde


class CargoForm(BootstrapMixin, forms.ModelForm):
    """Datos laborales que gestiona RR.HH. (RF26). Los datos de la cuenta y el rol los edita el administrador."""

    class Meta:
        model = get_user_model()
        fields = ['cargo']


# ---------- Permisos, vacaciones y feriados (RF27, RF28) ----------

class AusenciaForm(BootstrapMixin, forms.ModelForm):
    usuario = EmpleadoChoiceField(label='Empleado', queryset=None, empty_label='Seleccione un empleado')

    class Meta:
        model = Ausencia
        fields = ['usuario', 'tipo', 'desde', 'hasta', 'motivo']
        widgets = {'desde': FECHA, 'hasta': FECHA}

    def __init__(self, *args, registrado_por=None, **kwargs):
        super().__init__(*args, **kwargs)
        from .calculo import personal
        self.fields['usuario'].queryset = personal()
        self.instance.registrado_por = registrado_por


class FeriadoForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Feriado
        fields = ['fecha', 'nombre']
        widgets = {'fecha': FECHA}


# ---------- Reportes (RF20) ----------

class ReporteForm(BootstrapMixin, forms.Form):
    desde = forms.DateField(widget=FECHA)
    hasta = forms.DateField(widget=FECHA)
    sucursal = forms.ModelChoiceField(queryset=Sucursal.objects.filter(activa=True), required=False,
                                      empty_label='Todas las sucursales')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = timezone.localdate()
        self.fields['desde'].initial = hoy.replace(day=1)
        self.fields['hasta'].initial = hoy

    def clean(self):
        datos = super().clean()
        desde, hasta = datos.get('desde'), datos.get('hasta')
        if desde and hasta:
            if desde > hasta:
                self.add_error('hasta', 'Debe ser igual o posterior a «desde».')
            elif (hasta - desde).days > 366:
                self.add_error('hasta', 'El período no puede superar un año.')
        return datos

    def periodo(self):
        """(desde, hasta, sucursal) validados, o los de por defecto (mes en curso, todas las sucursales)."""
        if self.is_bound and self.is_valid():
            return self.cleaned_data['desde'], self.cleaned_data['hasta'], self.cleaned_data['sucursal']
        return self.fields['desde'].initial, self.fields['hasta'].initial, None

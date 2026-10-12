from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import Group

from .models import Sucursal, Usuario


class BootstrapMixin:
    """Aplica las clases de Bootstrap 5 a los widgets del formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput):
                clase = 'form-check-input'
            elif isinstance(widget, forms.Select):
                clase = 'form-select'
            else:
                clase = 'form-control'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {clase}".strip()

    def is_valid(self):
        valido = super().is_valid()
        for nombre in self.errors:
            if nombre in self.fields:
                self.fields[nombre].widget.attrs['class'] += ' is-invalid'
        return valido


class LoginForm(BootstrapMixin, AuthenticationForm):
    error_messages = {
        'invalid_login': 'Usuario, correo o contraseña incorrectos, o la cuenta está desactivada.',
        'inactive': 'La cuenta está desactivada.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario o correo'


class CambiarClaveForm(BootstrapMixin, PasswordChangeForm):
    pass


class ResetearClaveForm(BootstrapMixin, SetPasswordForm):
    pass


class UsuarioForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'ci', 'email', 'telefono', 'username', 'rol', 'sucursal']
        labels = {'first_name': 'Nombres', 'last_name': 'Apellidos', 'username': 'Nombre de usuario'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre in ('first_name', 'last_name', 'ci', 'email', 'rol'):
            self.fields[nombre].required = True
        self.fields['rol'].queryset = Group.objects.order_by('name')
        self.fields['sucursal'].queryset = Sucursal.objects.filter(activa=True)
        self.fields['rol'].empty_label = 'Seleccione un rol'
        self.fields['sucursal'].empty_label = 'Sin sucursal'
        self.fields['sucursal'].help_text = 'Necesaria para abrir caja y marcar asistencia.'
        self.fields['username'].help_text = 'Letras, números y @ . + - _ (máximo 150 caracteres).'

    def _no_duplicado(self, campo, valor, mensaje):
        existe = Usuario.objects.filter(**{f'{campo}__iexact': valor}).exclude(pk=self.instance.pk).exists()
        if existe:
            raise forms.ValidationError(mensaje)
        return valor

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        return self._no_duplicado('username', username, 'Ya existe un usuario con este nombre de usuario.')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        return self._no_duplicado('email', email, 'Ya existe un usuario con este correo.')

    def clean_ci(self):
        ci = self.cleaned_data['ci'].strip().upper()
        return self._no_duplicado('ci', ci, 'Ya existe un usuario con este CI.')

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip()


class UsuarioCrearForm(UsuarioForm):
    password1 = forms.CharField(
        label='Contraseña inicial', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='El usuario deberá cambiarla en su primer inicio de sesión.',
    )
    password2 = forms.CharField(
        label='Confirmar contraseña', strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean(self):
        datos = super().clean()
        p1, p2 = datos.get('password1'), datos.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        elif p1:
            # Se validan contra los datos del formulario (nombre, correo) para evitar contraseñas parecidas.
            for campo in ('username', 'first_name', 'last_name', 'email'):
                if campo in datos:
                    setattr(self.instance, campo, datos[campo])
            try:
                password_validation.validate_password(p1, self.instance)
            except forms.ValidationError as error:
                self.add_error('password1', error)
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password1'])
        usuario.debe_cambiar_clave = True
        usuario.is_active = True
        if commit:
            usuario.save()
        return usuario


class SucursalForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Sucursal
        fields = ['nombre', 'direccion', 'latitud', 'longitud', 'radio_metros', 'activa']
        help_texts = {
            'latitud': 'Por ejemplo, -19.047500. Se obtiene con clic derecho sobre el lugar en Google Maps.',
            'longitud': 'Por ejemplo, -65.259300.',
        }

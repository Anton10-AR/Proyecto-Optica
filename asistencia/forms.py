from django import forms


class MarcacionForm(forms.Form):
    latitud = forms.DecimalField(min_value=-90, max_value=90)
    longitud = forms.DecimalField(min_value=-180, max_value=180)

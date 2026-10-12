from django.contrib import admin

from .models import Marcacion


@admin.register(Marcacion)
class MarcacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'fecha_hora', 'sucursal', 'distancia_metros')
    list_filter = ('tipo', 'sucursal')

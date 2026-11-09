from django.contrib import admin

from .models import AsignacionHorario, Ausencia, Feriado, Horario, Marcacion, TramoHorario


@admin.register(Marcacion)
class MarcacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'fecha_hora', 'sucursal', 'distancia_metros')
    list_filter = ('tipo', 'sucursal')


class TramoInline(admin.TabularInline):
    model = TramoHorario
    extra = 0


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    inlines = [TramoInline]


@admin.register(AsignacionHorario)
class AsignacionHorarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'horario', 'desde')
    list_filter = ('horario',)


@admin.register(Ausencia)
class AusenciaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'desde', 'hasta')
    list_filter = ('tipo',)


@admin.register(Feriado)
class FeriadoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'nombre')

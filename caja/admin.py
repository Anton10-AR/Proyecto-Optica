from django.contrib import admin

from .models import MovimientoCaja, SesionCaja


class MovimientoInline(admin.TabularInline):
    model = MovimientoCaja
    extra = 0
    can_delete = False
    readonly_fields = ('fecha', 'usuario', 'tipo', 'forma_pago', 'monto', 'concepto')


@admin.register(SesionCaja)
class SesionCajaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'usuario', 'sucursal', 'estado', 'fecha_apertura', 'fecha_cierre', 'monto_contado')
    list_filter = ('estado', 'sucursal')
    inlines = [MovimientoInline]

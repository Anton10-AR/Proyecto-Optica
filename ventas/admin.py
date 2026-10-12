from django.contrib import admin

from .models import Pago, Venta


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    can_delete = False
    readonly_fields = ('fecha', 'usuario', 'monto', 'forma_pago', 'movimiento_caja')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'vendedor', 'sucursal', 'cliente_nombre', 'total', 'estado')
    list_filter = ('estado', 'sucursal')
    inlines = [PagoInline]

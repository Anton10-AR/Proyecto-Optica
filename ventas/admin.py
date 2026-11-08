from django.contrib import admin

from inventario.admin import SoloLecturaMixin

from .models import DetalleVenta, Pago, Venta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    can_delete = False
    readonly_fields = ('articulo', 'cantidad', 'precio_unitario', 'costo_unitario')

    def has_add_permission(self, request, obj=None):
        return False


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    can_delete = False
    readonly_fields = ('fecha', 'usuario', 'monto', 'forma_pago', 'movimiento_caja')


@admin.register(Venta)
class VentaAdmin(SoloLecturaMixin, admin.ModelAdmin):
    """Solo lectura: registrar, cobrar y anular pasan por ventas.servicios para mover stock y caja."""

    list_display = ('numero', 'fecha', 'vendedor', 'sucursal', 'cliente_nombre', 'total', 'estado')
    list_filter = ('estado', 'sucursal')
    inlines = [DetalleVentaInline, PagoInline]

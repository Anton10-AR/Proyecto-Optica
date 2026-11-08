from django.contrib import admin

from inventario.admin import SoloLecturaMixin

from .models import Cliente, DetalleVenta, EventoOrden, OrdenTrabajo, Pago, Receta, Venta


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


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ci_nit', 'telefono', 'correo')
    search_fields = ('nombre', 'ci_nit')


@admin.register(Receta)
class RecetaAdmin(SoloLecturaMixin, admin.ModelAdmin):
    """Una receta no se edita: una graduación nueva es una receta nueva."""

    list_display = ('cliente', 'fecha', 'origen', 'optico', 'medico')
    list_filter = ('origen',)
    search_fields = ('cliente__nombre',)


class EventoOrdenInline(admin.TabularInline):
    model = EventoOrden
    extra = 0
    can_delete = False
    readonly_fields = ('fecha', 'estado', 'usuario', 'nota')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(SoloLecturaMixin, admin.ModelAdmin):
    """Solo lectura: el estado cambia con ventas.servicios, que registra el historial."""

    list_display = ('numero', 'fecha', 'venta', 'estado', 'fecha_prometida')
    list_filter = ('estado',)
    inlines = [EventoOrdenInline]

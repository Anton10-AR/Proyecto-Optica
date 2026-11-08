from django.contrib import admin

from .models import (
    Ajuste, Articulo, Categoria, DetalleIngreso, DetalleTraspaso, Existencia, Ingreso, Movimiento, Proveedor, Traspaso,
)


class SoloLecturaMixin:
    """Los movimientos de stock se registran solo con inventario.servicios, nunca desde el admin."""

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'nit', 'contacto', 'telefono', 'activo')
    search_fields = ('razon_social', 'nit')


class ExistenciaInline(SoloLecturaMixin, admin.TabularInline):
    model = Existencia
    extra = 0
    readonly_fields = ('sucursal', 'cantidad')


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_venta', 'costo_promedio', 'stock_minimo', 'activo')
    list_filter = ('categoria', 'activo', 'controla_stock')
    search_fields = ('codigo', 'codigo_barras', 'nombre')
    readonly_fields = ('costo_promedio',)
    inlines = [ExistenciaInline]


class DetalleIngresoInline(SoloLecturaMixin, admin.TabularInline):
    model = DetalleIngreso
    extra = 0


@admin.register(Ingreso)
class IngresoAdmin(SoloLecturaMixin, admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'sucursal', 'proveedor', 'documento', 'usuario')
    inlines = [DetalleIngresoInline]


@admin.register(Ajuste)
class AjusteAdmin(SoloLecturaMixin, admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'tipo', 'articulo', 'sucursal', 'cantidad', 'motivo', 'usuario')
    list_filter = ('tipo', 'sucursal')


class DetalleTraspasoInline(SoloLecturaMixin, admin.TabularInline):
    model = DetalleTraspaso
    extra = 0


@admin.register(Traspaso)
class TraspasoAdmin(SoloLecturaMixin, admin.ModelAdmin):
    list_display = ('numero', 'fecha_envio', 'origen', 'destino', 'estado', 'usuario_envio', 'usuario_recepcion')
    list_filter = ('estado',)
    inlines = [DetalleTraspasoInline]


@admin.register(Movimiento)
class MovimientoAdmin(SoloLecturaMixin, admin.ModelAdmin):
    list_display = ('fecha', 'articulo', 'sucursal', 'tipo', 'cantidad', 'costo_unitario', 'saldo', 'costo_promedio',
                    'referencia')
    list_filter = ('tipo', 'sucursal')
    search_fields = ('articulo__codigo', 'articulo__nombre', 'referencia')

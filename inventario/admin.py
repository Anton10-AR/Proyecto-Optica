from django.contrib import admin

from .models import Articulo, Categoria, Existencia, Proveedor


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'nit', 'contacto', 'telefono', 'activo')
    search_fields = ('razon_social', 'nit')


class ExistenciaInline(admin.TabularInline):
    """Solo lectura: el stock se modifica con los movimientos de inventario, no a mano."""
    model = Existencia
    extra = 0
    can_delete = False
    readonly_fields = ('sucursal', 'cantidad')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_venta', 'costo_promedio', 'stock_minimo', 'activo')
    list_filter = ('categoria', 'activo', 'controla_stock')
    search_fields = ('codigo', 'codigo_barras', 'nombre')
    readonly_fields = ('costo_promedio',)
    inlines = [ExistenciaInline]

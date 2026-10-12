from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import RegistroActividad, Sucursal, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'ci', 'rol', 'sucursal', 'is_active')
    list_filter = ('rol', 'sucursal', 'is_active', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'ci', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos de la óptica', {'fields': ('ci', 'telefono', 'rol', 'sucursal', 'debe_cambiar_clave')}),
    )


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'latitud', 'longitud', 'radio_metros', 'activa')


@admin.register(RegistroActividad)
class RegistroActividadAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'accion', 'usuario', 'usuario_afectado', 'credencial', 'ip')
    list_filter = ('accion',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

"""Matriz de permisos por rol (RBAC).

Es la única fuente de verdad de qué puede hacer cada rol. El comando
`manage.py configurar_roles` crea los grupos y les asigna exactamente estos
permisos; `manage.py matriz_permisos` imprime la matriz para la documentación.
"""

from django.contrib.auth.models import Group, Permission
from django.db import transaction

ADMINISTRADOR = 'Administrador'
CAJERO_VENDEDOR = 'Cajero/Vendedor'
EMPLEADO = 'Empleado'
GERENTE = 'Gerente'
RRHH = 'Recursos Humanos'
ALMACEN = 'Encargado de almacén'
OPTICO = 'Óptico/Técnico de taller'

# Permisos agrupados por módulo, en el orden en que aparecen en la matriz.
PERMISOS = {
    'Usuarios': {
        'core.view_usuario': 'Ver y buscar usuarios',
        'core.add_usuario': 'Crear usuarios',
        'core.change_usuario': 'Editar, resetear contraseña y desactivar usuarios',
        'core.view_registroactividad': 'Ver el registro de actividad',
    },
    'Sucursales': {
        'core.view_sucursal': 'Ver sucursales',
        'core.add_sucursal': 'Crear sucursales',
        'core.change_sucursal': 'Editar sucursales',
    },
    'Caja': {
        'caja.operar_caja': 'Abrir su caja, registrar movimientos y cerrarla con arqueo',
        'caja.ver_todas_cajas': 'Ver las cajas de todos los usuarios',
    },
    'Ventas': {
        'ventas.registrar_venta': 'Registrar ventas y cobrar pagos',
        'ventas.ver_todas_ventas': 'Ver las ventas de todos los vendedores',
    },
    'Asistencia': {
        'asistencia.marcar_asistencia': 'Marcar su entrada/salida y ver su historial',
        'asistencia.ver_todas_marcaciones': 'Ver la asistencia de todo el personal',
    },
}
TODOS = [p for grupo in PERMISOS.values() for p in grupo]

ROLES = {
    ADMINISTRADOR: TODOS,
    GERENTE: [
        'core.view_usuario',
        'core.view_registroactividad',
        'core.view_sucursal',
        'caja.ver_todas_cajas',
        'ventas.ver_todas_ventas',
        'asistencia.marcar_asistencia',
        'asistencia.ver_todas_marcaciones',
    ],
    CAJERO_VENDEDOR: [
        'caja.operar_caja',
        'ventas.registrar_venta',
        'asistencia.marcar_asistencia',
    ],
    RRHH: [
        'core.view_usuario',
        'core.view_sucursal',
        'asistencia.marcar_asistencia',
        'asistencia.ver_todas_marcaciones',
    ],
    ALMACEN: [
        'asistencia.marcar_asistencia',
    ],
    OPTICO: [
        'asistencia.marcar_asistencia',
    ],
    EMPLEADO: [
        'asistencia.marcar_asistencia',
    ],
}


def _permiso(codigo):
    app_label, codename = codigo.split('.')
    return Permission.objects.get(content_type__app_label=app_label, codename=codename)


@transaction.atomic
def configurar_roles():
    """Crea los roles y deja a cada uno exactamente con los permisos de ROLES."""
    for nombre, codigos in ROLES.items():
        grupo, _ = Group.objects.get_or_create(name=nombre)
        grupo.permissions.set([_permiso(c) for c in codigos])

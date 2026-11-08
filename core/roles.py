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
    'Parámetros': {
        'core.change_configuracion': 'Definir los parámetros del negocio (anticipo mínimo)',
    },
    'Inventario': {
        'inventario.ver_articulos': 'Consultar artículos, precios y stock por sucursal',
        'inventario.gestionar_catalogo': 'Crear y editar artículos y categorías',
        'inventario.gestionar_proveedores': 'Ver, crear y editar proveedores',
        'inventario.registrar_ingresos': 'Registrar ingresos de mercadería por compra',
        'inventario.registrar_ajustes': 'Registrar bajas y ajustes por conteo físico',
        'inventario.enviar_traspasos': 'Enviar mercadería a otra sucursal',
        'inventario.recibir_traspasos': 'Confirmar la recepción de traspasos en su sucursal',
        'inventario.ver_kardex': 'Ver el kardex, los costos y los movimientos de inventario',
    },
    'Caja': {
        'caja.operar_caja': 'Abrir su caja, registrar movimientos y cerrarla con arqueo',
        'caja.ver_todas_cajas': 'Ver las cajas de todos los usuarios',
    },
    'Ventas': {
        'ventas.registrar_venta': 'Registrar ventas y cobrar pagos',
        'ventas.ver_todas_ventas': 'Ver las ventas de todos los vendedores',
        'ventas.anular_venta': 'Anular ventas (repone el stock y devuelve lo pagado desde su caja)',
    },
    'Clientes y recetas': {
        'ventas.gestionar_clientes': 'Registrar y editar clientes',
        'ventas.registrar_receta': 'Registrar recetas de los clientes',
        'ventas.realizar_examen': 'Realizar exámenes visuales (figurar como óptico responsable)',
    },
    'Órdenes de trabajo': {
        'ventas.ver_ordenes': 'Consultar las órdenes de trabajo',
        'ventas.actualizar_ordenes': 'Pasar las órdenes al taller y marcarlas como listas',
        'ventas.entregar_ordenes': 'Entregar los trabajos al cliente',
        'ventas.autorizar_entrega_con_saldo': 'Autorizar la entrega de un trabajo con saldo pendiente',
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
        'inventario.ver_articulos',
        'inventario.ver_kardex',
        'caja.operar_caja',  # para devolver lo pagado al anular una venta
        'caja.ver_todas_cajas',
        'ventas.ver_todas_ventas',
        'ventas.anular_venta',
        'ventas.ver_ordenes',
        'ventas.autorizar_entrega_con_saldo',
        'core.change_configuracion',
        'asistencia.marcar_asistencia',
        'asistencia.ver_todas_marcaciones',
    ],
    CAJERO_VENDEDOR: [
        'inventario.ver_articulos',
        'inventario.recibir_traspasos',
        'caja.operar_caja',
        'ventas.registrar_venta',
        'ventas.gestionar_clientes',
        'ventas.registrar_receta',
        'ventas.ver_ordenes',
        'ventas.entregar_ordenes',
        'asistencia.marcar_asistencia',
    ],
    RRHH: [
        'core.view_usuario',
        'core.view_sucursal',
        'asistencia.marcar_asistencia',
        'asistencia.ver_todas_marcaciones',
    ],
    ALMACEN: [
        'inventario.ver_articulos',
        'inventario.gestionar_catalogo',
        'inventario.gestionar_proveedores',
        'inventario.registrar_ingresos',
        'inventario.registrar_ajustes',
        'inventario.enviar_traspasos',
        'inventario.recibir_traspasos',
        'inventario.ver_kardex',
        'asistencia.marcar_asistencia',
    ],
    OPTICO: [
        'inventario.ver_articulos',
        'ventas.gestionar_clientes',
        'ventas.registrar_receta',
        'ventas.realizar_examen',
        'ventas.ver_ordenes',
        'ventas.actualizar_ordenes',
        'ventas.entregar_ordenes',
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

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from asistencia.models import Marcacion
from caja.models import FormaPago, MovimientoCaja, SesionCaja
from core import roles
from core.models import Sucursal, Usuario
from ventas.models import Pago, Venta

CLAVE_PRUEBA = 'Casimiro2026!'

# Coordenadas de prueba en el centro de Sucre; ajústelas a la ubicación real de cada sucursal.
SUCURSALES = [
    ('Sucursal Centro', 'Dirección de prueba 1, Sucre', Decimal('-19.047500'), Decimal('-65.259300')),
    ('Sucursal Norte', 'Dirección de prueba 2, Sucre', Decimal('-19.033000'), Decimal('-65.262500')),
]

# usuario, nombres, apellidos, CI, teléfono, rol, índice de sucursal, activo
USUARIOS = [
    ('admin', 'Sofía', 'Torrico Lima', '1000001', '70000001', roles.ADMINISTRADOR, 0, True),
    ('gerente', 'Daniel', 'Ortiz Paredes', '1000002', '70000002', roles.GERENTE, 0, True),
    ('cajero1', 'Juan', 'Pérez Mamani', '1000003', '70000003', roles.CAJERO_VENDEDOR, 0, True),
    ('cajero2', 'Lucía', 'Quispe Vargas', '1000004', '70000004', roles.CAJERO_VENDEDOR, 1, True),
    ('rrhh', 'Valeria', 'Ramos Soliz', '1000005', '70000005', roles.RRHH, 0, True),
    ('almacen', 'Pedro', 'Rojas Torrez', '1000006', '70000006', roles.ALMACEN, 0, True),
    ('optico', 'Marta', 'Gutiérrez Choque', '1000007', '70000007', roles.OPTICO, 0, True),
    ('empleado1', 'Luis', 'Fernández Cruz', '1000008', '70000008', roles.EMPLEADO, 0, True),
    ('empleado2', 'Ana', 'Mendoza Arce', '1000009', '70000009', roles.EMPLEADO, 1, True),
    ('exempleado', 'Jorge', 'Salazar Ríos', '1000010', '70000010', roles.EMPLEADO, 0, False),
]


class Command(BaseCommand):
    help = 'Crea roles, sucursales, usuarios de cada rol y operaciones de ejemplo para demostraciones.'

    @transaction.atomic
    def handle(self, *args, **options):
        roles.configurar_roles()
        sucursales = []
        for nombre, direccion, lat, lon in SUCURSALES:
            sucursal, _ = Sucursal.objects.update_or_create(
                nombre=nombre, defaults={'direccion': direccion, 'latitud': lat, 'longitud': lon, 'radio_metros': 150},
            )
            sucursales.append(sucursal)

        usuarios = {}
        for username, nombres, apellidos, ci, telefono, rol, suc, activo in USUARIOS:
            usuario, _ = Usuario.objects.update_or_create(username=username, defaults={
                'first_name': nombres, 'last_name': apellidos, 'ci': ci, 'telefono': telefono,
                'email': f'{username}@opticascasimiro.test', 'rol': Group.objects.get(name=rol),
                'sucursal': sucursales[suc], 'is_active': activo, 'debe_cambiar_clave': False,
            })
            usuario.set_password(CLAVE_PRUEBA)
            usuario.save()
            usuarios[username] = usuario

        self._operaciones_de_ejemplo(usuarios)

        self.stdout.write(self.style.SUCCESS(
            f'Datos de prueba cargados. Usuarios: {", ".join(usuarios)}. Contraseña de todos: {CLAVE_PRUEBA}'
        ))
        self.stdout.write('La cuenta "exempleado" está desactivada para demostrar la baja lógica.')

    def _operaciones_de_ejemplo(self, usuarios):
        """Una caja cerrada con una venta y marcaciones de ayer, para que los historiales no estén vacíos."""
        cajero, empleado = usuarios['cajero1'], usuarios['empleado1']
        if SesionCaja.objects.filter(usuario=cajero).exists():
            return
        ayer = timezone.now() - timedelta(days=1)
        sesion = SesionCaja.objects.create(usuario=cajero, sucursal=cajero.sucursal, monto_inicial=Decimal('200'))
        venta = Venta.objects.create(
            vendedor=cajero, sucursal=cajero.sucursal, cliente_nombre='Cliente de prueba', cliente_ci='5555555',
            descripcion='Armazón y lunas monofocales', total=Decimal('650'),
        )
        movimiento = MovimientoCaja.objects.create(
            sesion=sesion, usuario=cajero, tipo=MovimientoCaja.Tipo.INGRESO, forma_pago=FormaPago.EFECTIVO,
            monto=Decimal('350'), concepto=f'Pago de la nota de venta {venta.numero}',
        )
        Pago.objects.create(venta=venta, usuario=cajero, movimiento_caja=movimiento,
                            monto=Decimal('350'), forma_pago=FormaPago.EFECTIVO)
        sesion.monto_esperado = sesion.efectivo_esperado
        sesion.monto_contado = Decimal('550')
        sesion.estado = SesionCaja.Estado.CERRADA
        sesion.fecha_cierre = timezone.now()
        sesion.save()
        SesionCaja.objects.filter(pk=sesion.pk).update(fecha_apertura=ayer)

        sucursal = empleado.sucursal
        for tipo, hora in ((Marcacion.Tipo.ENTRADA, 8), (Marcacion.Tipo.SALIDA, 12),
                           (Marcacion.Tipo.ENTRADA, 14), (Marcacion.Tipo.SALIDA, 19)):
            marcacion = Marcacion.objects.create(
                usuario=empleado, sucursal=sucursal, tipo=tipo,
                latitud=sucursal.latitud, longitud=sucursal.longitud, distancia_metros=0,
            )
            momento = timezone.localtime(ayer).replace(hour=hora, minute=30, second=0, microsecond=0)
            Marcacion.objects.filter(pk=marcacion.pk).update(fecha_hora=momento)

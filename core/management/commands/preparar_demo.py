from io import StringIO

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from asistencia.models import Marcacion
from caja.models import MovimientoCaja, SesionCaja
from core.models import RegistroActividad, Sucursal, Usuario
from inventario.models import Ajuste, Articulo, Categoria, Existencia, Ingreso, Movimiento, Proveedor, Traspaso
from ventas.models import Pago, Venta

from .cargar_datos_prueba import ARTICULOS, CATEGORIAS, CLAVE_PRUEBA, PROVEEDORES, SUCURSALES, USUARIOS


class Command(BaseCommand):
    help = ('Deja la base en el estado inicial de la demostración: borra las operaciones (ventas, cajas, '
            'marcaciones, existencias, auditoría y sesiones), el catálogo y los usuarios creados en ensayos, '
            'y recarga los datos de prueba. '
            'Los superusuarios se conservan.')

    def add_arguments(self, parser):
        parser.add_argument('--si', action='store_true', help='No pedir confirmación.')

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Por seguridad, solo se ejecuta con DJANGO_DEBUG=True (entorno de desarrollo o demostración).')
        if not options['si']:
            respuesta = input('Se borrarán TODAS las ventas, cajas, marcaciones, existencias y la auditoría, y el catálogo y los usuarios de ensayo '
                              f'de la base "{settings.DATABASES["default"]["NAME"]}". ¿Continuar? [si/no]: ')
            if respuesta.strip().lower() not in ('si', 'sí', 's'):
                self.stdout.write('Cancelado.')
                return

        with transaction.atomic():
            borrados = {
                'pagos': Pago.objects.all().delete()[0],
                'ventas': Venta.objects.all().delete()[0],
                'movimientos de caja': MovimientoCaja.objects.all().delete()[0],
                'cajas': SesionCaja.objects.all().delete()[0],
                'marcaciones': Marcacion.objects.all().delete()[0],
                'registros de auditoría': RegistroActividad.objects.all().delete()[0],
                'sesiones abiertas': Session.objects.all().delete()[0],
                'movimientos de inventario': Movimiento.objects.all().delete()[0],
                'ingresos': Ingreso.objects.all().delete()[0],
                'bajas y ajustes': Ajuste.objects.all().delete()[0],
                'traspasos': Traspaso.objects.all().delete()[0],
                'existencias': Existencia.objects.all().delete()[0],
            }
            # Sin movimientos, el costo promedio vuelve a cero; las compras de prueba lo recalculan.
            Articulo.objects.update(costo_promedio=0)
            # El catálogo creado en ensayos se borra; el de prueba se restaura con cargar_datos_prueba.
            borrados['artículos de ensayo'] = Articulo.objects.exclude(codigo__in=[a[0] for a in ARTICULOS]).delete()[0]
            de_prueba = [u[0] for u in USUARIOS]
            ensayo = Usuario.objects.filter(is_superuser=False).exclude(username__in=de_prueba)
            borrados['usuarios de ensayo'] = len([u.delete() for u in ensayo])
            sucursales = [s[0] for s in SUCURSALES]
            borrados['sucursales de ensayo'] = Sucursal.objects.exclude(nombre__in=sucursales).filter(
                usuarios__isnull=True).delete()[0]
            call_command('cargar_datos_prueba', stdout=StringIO())
            # Después de restaurar el catálogo, ningún artículo de prueba apunta ya a estos registros de ensayo.
            borrados['proveedores de ensayo'] = Proveedor.objects.exclude(
                razon_social__in=[p[0] for p in PROVEEDORES]).delete()[0]
            borrados['categorías de ensayo'] = Categoria.objects.exclude(nombre__in=[c[0] for c in CATEGORIAS]).delete()[0]

        for nombre, cantidad in borrados.items():
            if cantidad:
                self.stdout.write(f'  Borrados: {cantidad} {nombre}')
        self.stdout.write(self.style.SUCCESS('\nDemostración lista.'))
        self.stdout.write(f'Contraseña de los usuarios de prueba: {CLAVE_PRUEBA}')
        self.stdout.write('Usuarios: ' + ', '.join(f'{u[0]} ({u[5]})' for u in USUARIOS))
        self.stdout.write('\nPara marcar asistencia, la ubicación debe estar dentro del radio de la sucursal. '
                          'Fuera de ella, simúlela en Chrome/Edge (F12 → ⋮ → More tools → Sensors → Location):')
        for nombre, _, lat, lon, radio in SUCURSALES:
            self.stdout.write(f'  {nombre}: latitud {lat}, longitud {lon} (radio {radio} m)')

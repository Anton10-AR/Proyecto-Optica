from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from asistencia.models import Marcacion
from caja.models import FormaPago, MovimientoCaja, SesionCaja
from core import roles
from core.models import Sucursal, Usuario
from inventario import servicios as inventario
from inventario.models import Ajuste, Articulo, Categoria, Movimiento, Proveedor
from ventas.models import Cliente, DetalleVenta, EventoOrden, OrdenTrabajo, Pago, Receta, Venta

CLAVE_PRUEBA = 'Casimiro2026!'

# nombre, dirección, latitud, longitud, radio de marcación (m).
# Para las pruebas, ambas sucursales están en la Facultad de Ciencias y Tecnología (USFX), donde se hace la
# demostración, con un radio amplio porque la ubicación de una laptop por Wi-Fi puede errar en cientos de metros.
SUCURSALES = [
    ('Sucursal Centro', 'Dirección de prueba 1, Sucre', Decimal('-19.039699'), Decimal('-65.256900'), 300),
    ('Sucursal Norte', 'Dirección de prueba 2, Sucre', Decimal('-19.039699'), Decimal('-65.256900'), 300),
]

# usuario, nombres, apellidos, CI, teléfono, rol, índice de sucursal, activo
USUARIOS = [
    ('administrador', 'Sofía', 'Torrico Lima', '1000001', '70000001', roles.ADMINISTRADOR, 0, True),
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

CATEGORIAS = [
    ('Armazones', 'Monturas de metal, acetato y al aire'),
    ('Lunas', 'Por tipo de material, diseño y tratamiento; la graduación va en la receta'),
    ('Lentes de contacto', ''),
    ('Accesorios', 'Estuches, paños, líquidos y cordones'),
    ('Servicios', 'Examen visual y trabajos de taller; no controlan stock'),
]

# razón social, NIT, contacto, teléfono
PROVEEDORES = [
    ('Distribuidora Óptica Andina SRL', '1023456019', 'Carla Méndez', '72800001'),
    ('Lunas y Lentes Bolivia SA', '2034567018', 'Marco Céspedes', '72800002'),
]

# código, código de barras, nombre, categoría, marca, índice de proveedor, precio, stock mínimo, controla stock
ARTICULOS = [
    ('ARM-001', '7790000000011', 'Armazón metálico rectangular', 'Armazones', 'Vision Pro', 0, '350.00', 2, True),
    ('ARM-002', '7790000000028', 'Armazón de acetato redondo', 'Armazones', 'Urban', 0, '280.00', 2, True),
    ('LUN-001', None, 'Luna monofocal CR-39 antirreflejo', 'Lunas', '', 1, '180.00', 6, True),
    ('LUN-002', None, 'Luna progresiva policarbonato fotocromática', 'Lunas', '', 1, '650.00', 4, True),
    ('LCO-001', '7790000000035', 'Lentes de contacto mensuales (caja de 6)', 'Lentes de contacto', 'AquaSoft', 1, '220.00', 3, True),
    ('ACC-001', '7790000000042', 'Estuche rígido con paño', 'Accesorios', '', 0, '35.00', 10, True),
    ('ACC-002', '7790000000059', 'Líquido limpiador 60 ml', 'Accesorios', '', 0, '25.00', 10, True),
    ('SRV-001', None, 'Examen visual computarizado', 'Servicios', '', None, '50.00', 0, False),
    ('SRV-002', None, 'Montaje de lunas en armazón propio', 'Servicios', '', None, '40.00', 0, False),
]


# Lunas que se tallan según la receta: su venta exige receta, anticipo mínimo y genera una orden de trabajo.
LENTES_GRADUADOS = {'LUN-001', 'LUN-002'}

# nombre, CI/NIT, teléfono, fecha de nacimiento (año, mes, día)
CLIENTES = [
    ('María Fernanda López Rojas', '5555555', '71234567', (1990, 4, 12)),
    ('Carlos Andrés Vargas Soliz', '6666601', '72345678', (1968, 9, 3)),
    ('Rosa Elena Quiroga Mendoza', '7777702', '', None),
]


class Command(BaseCommand):
    help = 'Crea roles, sucursales, usuarios de cada rol y operaciones de ejemplo para demostraciones.'

    @transaction.atomic
    def handle(self, *args, **options):
        roles.configurar_roles()
        sucursales = []
        for nombre, direccion, lat, lon, radio in SUCURSALES:
            sucursal, _ = Sucursal.objects.update_or_create(
                nombre=nombre, defaults={'direccion': direccion, 'latitud': lat, 'longitud': lon, 'radio_metros': radio},
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

        self._catalogo()
        self._inventario_inicial(usuarios, sucursales)
        self._clientes(usuarios)
        self._operaciones_de_ejemplo(usuarios)

        self.stdout.write(self.style.SUCCESS(
            f'Datos de prueba cargados. Usuarios: {", ".join(usuarios)}. Contraseña de todos: {CLAVE_PRUEBA}'
        ))
        self.stdout.write('La cuenta "exempleado" está desactivada para demostrar la baja lógica.')

    def _catalogo(self):
        categorias = {}
        for nombre, descripcion in CATEGORIAS:
            categorias[nombre], _ = Categoria.objects.update_or_create(
                nombre=nombre, defaults={'descripcion': descripcion, 'activa': True})
        proveedores = [
            Proveedor.objects.update_or_create(razon_social=razon, defaults={
                'nit': nit, 'contacto': contacto, 'telefono': telefono, 'activo': True})[0]
            for razon, nit, contacto, telefono in PROVEEDORES
        ]
        for codigo, barras, nombre, categoria, marca, proveedor, precio, minimo, controla in ARTICULOS:
            Articulo.objects.update_or_create(codigo=codigo, defaults={
                'codigo_barras': barras, 'nombre': nombre, 'categoria': categorias[categoria], 'marca': marca,
                'proveedor': proveedores[proveedor] if proveedor is not None else None,
                'precio_venta': Decimal(precio), 'stock_minimo': minimo, 'controla_stock': controla, 'activo': True,
                'requiere_receta': codigo in LENTES_GRADUADOS,
            })

    def _clientes(self, usuarios):
        """Clientes con su historial de recetas: una de examen en la óptica y una externa (RF21, RF22)."""
        clientes = [
            Cliente.objects.update_or_create(ci_nit=ci, defaults={
                'nombre': nombre, 'telefono': telefono,
                'fecha_nacimiento': date(*nacimiento) if nacimiento else None,
            })[0]
            for nombre, ci, telefono, nacimiento in CLIENTES
        ]
        if Receta.objects.exists():
            return
        maria, carlos, _ = clientes
        optico, cajero = usuarios['optico'], usuarios['cajero1']
        hoy = timezone.localdate()
        # La receta anterior de María, de hace un año, muestra que el historial guarda cada graduación.
        Receta.objects.create(
            cliente=maria, fecha=hoy - timedelta(days=380), origen=Receta.Origen.EXAMEN, optico=optico,
            od_esfera=Decimal('-1.00'), od_cilindro=Decimal('-0.25'), od_eje=180,
            oi_esfera=Decimal('-0.75'), distancia_pupilar=Decimal('62'), registrado_por=optico)
        Receta.objects.create(
            cliente=maria, fecha=hoy - timedelta(days=2), origen=Receta.Origen.EXAMEN, optico=optico,
            od_esfera=Decimal('-1.25'), od_cilindro=Decimal('-0.50'), od_eje=180,
            oi_esfera=Decimal('-1.00'), oi_cilindro=Decimal('-0.25'), oi_eje=170,
            distancia_pupilar=Decimal('62'), observaciones='Uso permanente. Control en un año.', registrado_por=optico)
        Receta.objects.create(
            cliente=carlos, fecha=hoy - timedelta(days=10), origen=Receta.Origen.EXTERNA,
            medico='Dr. Mario Salinas · Clínica Oftalmológica Sucre',
            od_esfera=Decimal('1.50'), od_adicion=Decimal('2.00'), oi_esfera=Decimal('1.75'), oi_adicion=Decimal('2.00'),
            distancia_pupilar=Decimal('64'), observaciones='Presbicia. Sugiere lentes progresivos.',
            registrado_por=cajero)

    def _inventario_inicial(self, usuarios, sucursales):
        """Compras, traspasos y una baja hechos con los servicios, para que el kardex y el stock tengan datos."""
        if Movimiento.objects.exists():
            return
        almacen, cajero_norte = usuarios['almacen'], usuarios['cajero2']
        centro, norte = sucursales
        andina, lunas = (Proveedor.objects.get(razon_social=p[0]) for p in PROVEEDORES)
        art = {a.codigo: a for a in Articulo.objects.all()}

        inventario.registrar_ingreso(almacen, centro, andina, [
            (art['ARM-001'], 10, Decimal('150')), (art['ARM-002'], 8, Decimal('110')),
            (art['ACC-001'], 30, Decimal('12')), (art['ACC-002'], 12, Decimal('9')),
        ], documento='F-0001520')
        inventario.registrar_ingreso(almacen, centro, lunas, [
            (art['LUN-001'], 40, Decimal('60')), (art['LUN-002'], 12, Decimal('260')),
            (art['LCO-001'], 15, Decimal('120')),
        ], documento='F-0098211')
        # Segunda compra a otro costo: el promedio de ARM-001 pasa a (10 x 150 + 6 x 170) / 16 = 157,50.
        inventario.registrar_ingreso(almacen, centro, andina, [(art['ARM-001'], 6, Decimal('170'))],
                                     documento='F-0001587')
        recibido = inventario.enviar_traspaso(almacen, centro, norte, [
            (art['ARM-001'], 4), (art['LUN-001'], 12), (art['ACC-001'], 8),
        ], observacion='Reposición semanal')
        inventario.recibir_traspaso(recibido, cajero_norte)
        inventario.enviar_traspaso(almacen, centro, norte, [(art['ARM-002'], 3), (art['ACC-002'], 2)],
                                   observacion='Pedido de la sucursal')
        inventario.registrar_ajuste(almacen, centro, art['ARM-002'], Ajuste.Tipo.BAJA, 1,
                                    'Armazón con la bisagra rota al exhibirlo')

    def _operaciones_de_ejemplo(self, usuarios):
        """Una caja cerrada con una venta y marcaciones de ayer, para que los historiales no estén vacíos."""
        cajero, empleado = usuarios['cajero1'], usuarios['empleado1']
        if SesionCaja.objects.filter(usuario=cajero).exists():
            return
        ayer = timezone.localtime() - timedelta(days=1)

        def a_las(hora, minuto=0):
            return ayer.replace(hour=hora, minute=minuto, second=0, microsecond=0)

        sesion = SesionCaja.objects.create(usuario=cajero, sucursal=cajero.sucursal, monto_inicial=Decimal('200'))
        # Armazón (350) + 2 lunas (2 × 180) = 710, con un descuento de 60: total 650, anticipo 350, saldo 300.
        # Las lunas son lentes graduados: la venta lleva la receta de la clienta y una orden de trabajo.
        armazon, luna = Articulo.objects.get(codigo='ARM-001'), Articulo.objects.get(codigo='LUN-001')
        clienta = Cliente.objects.get(ci_nit=CLIENTES[0][1])
        venta = Venta.objects.create(
            vendedor=cajero, sucursal=cajero.sucursal, cliente=clienta, cliente_nombre=clienta.nombre,
            cliente_ci=clienta.ci_nit, descuento=Decimal('60'), total=Decimal('650'),
        )
        salidas = inventario.registrar_salida_venta(cajero, cajero.sucursal, [(armazon, 1), (luna, 2)], str(venta))
        DetalleVenta.objects.bulk_create([
            DetalleVenta(venta=venta, articulo=a, cantidad=c, precio_unitario=a.precio_venta,
                         costo_unitario=salidas[a.pk].costo_unitario)
            for a, c in ((armazon, 1), (luna, 2))
        ])
        movimiento = MovimientoCaja.objects.create(
            sesion=sesion, usuario=cajero, tipo=MovimientoCaja.Tipo.INGRESO, forma_pago=FormaPago.EFECTIVO,
            monto=Decimal('350'), concepto=f'Pago de la nota de venta {venta.numero}',
        )
        pago = Pago.objects.create(venta=venta, usuario=cajero, movimiento_caja=movimiento,
                                   monto=Decimal('350'), forma_pago=FormaPago.EFECTIVO)
        sesion.monto_esperado = sesion.efectivo_esperado
        sesion.monto_contado = Decimal('550')
        sesion.estado = SesionCaja.Estado.CERRADA
        sesion.fecha_cierre = a_las(19, 30)
        sesion.save()
        # Las fechas con auto_now_add se corrigen con update() para que toda la operación quede en el día anterior.
        SesionCaja.objects.filter(pk=sesion.pk).update(fecha_apertura=a_las(8, 30))
        Venta.objects.filter(pk=venta.pk).update(fecha=a_las(10, 15))
        MovimientoCaja.objects.filter(pk=movimiento.pk).update(fecha=a_las(10, 15))
        Pago.objects.filter(pk=pago.pk).update(fecha=a_las(10, 15))

        # La orden ya está lista, pero la venta tiene saldo: sirve para demostrar que la entrega exige cobrar el
        # saldo o la autorización del gerente (RF31).
        orden = OrdenTrabajo.objects.create(venta=venta, receta=clienta.recetas.first(),
                                            fecha_prometida=timezone.localdate() + timedelta(days=1),
                                            estado=OrdenTrabajo.Estado.LISTO)
        OrdenTrabajo.objects.filter(pk=orden.pk).update(fecha=a_las(10, 15))
        optico = usuarios['optico']
        for estado, usuario, hora, nota in (
                (OrdenTrabajo.Estado.PENDIENTE, cajero, (10, 15), f'Generada con la {venta}.'),
                (OrdenTrabajo.Estado.EN_TALLER, optico, (11, 0), ''),
                (OrdenTrabajo.Estado.LISTO, optico, (17, 40), 'Lunas talladas y montadas.')):
            evento = EventoOrden.objects.create(orden=orden, estado=estado, usuario=usuario, nota=nota)
            EventoOrden.objects.filter(pk=evento.pk).update(fecha=a_las(*hora))

        sucursal = empleado.sucursal
        for tipo, hora in ((Marcacion.Tipo.ENTRADA, 8), (Marcacion.Tipo.SALIDA, 12),
                           (Marcacion.Tipo.ENTRADA, 14), (Marcacion.Tipo.SALIDA, 19)):
            marcacion = Marcacion.objects.create(
                usuario=empleado, sucursal=sucursal, tipo=tipo,
                latitud=sucursal.latitud, longitud=sucursal.longitud, distancia_metros=0,
            )
            Marcacion.objects.filter(pk=marcacion.pk).update(fecha_hora=a_las(hora, 30))

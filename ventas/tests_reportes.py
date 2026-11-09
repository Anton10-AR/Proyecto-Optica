"""Reportes de ventas por período, vendedor y producto (RF07)."""

from datetime import timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from caja.servicios import abrir_caja
from core import roles
from core.models import Sucursal
from core.tests import BaseTest, crear_usuario
from inventario import servicios as inventario
from inventario.models import Articulo, Categoria, Proveedor
from ventas import reportes, servicios
from ventas.models import Venta


class ReportesVentasTests(BaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.norte = Sucursal.objects.create(nombre='Norte', direccion='Calle 2', latitud=0, longitud=0)
        cls.gerente = crear_usuario('gerente', roles.GERENTE, cls.sucursal, ci='6666666')
        cls.cajero_norte = crear_usuario('cajeronorte', roles.CAJERO_VENDEDOR, cls.norte, ci='5555555')
        almacen = crear_usuario('almacen', roles.ALMACEN, cls.sucursal, ci='4444444')
        categoria = Categoria.objects.create(nombre='Ópticos')
        cls.armazon = Articulo.objects.create(codigo='ARM-1', nombre='Armazón', categoria=categoria,
                                              precio_venta=Decimal('300'))
        cls.estuche = Articulo.objects.create(codigo='ACC-1', nombre='Estuche', categoria=categoria,
                                              precio_venta=Decimal('40'))
        cls.examen = Articulo.objects.create(codigo='SRV-1', nombre='Examen', categoria=categoria,
                                             precio_venta=Decimal('50'), controla_stock=False)
        proveedor = Proveedor.objects.create(razon_social='Andina')
        for sucursal in (cls.sucursal, cls.norte):
            inventario.registrar_ingreso(almacen, sucursal, proveedor, [
                (cls.armazon, 10, Decimal('120')), (cls.estuche, 10, Decimal('10'))])

    def setUp(self):
        abrir_caja(self.cajero, Decimal('0'))
        abrir_caja(self.cajero_norte, Decimal('0'))
        abrir_caja(self.gerente, Decimal('1000'))
        # Centro: 300 + 40 = 340 con 40 de descuento → 300, pagado en efectivo.
        servicios.registrar_venta(self.cajero, [(self.armazon, 1), (self.estuche, 1)], Decimal('300'), 'EFECTIVO',
                                  cliente_nombre='Ana', descuento=Decimal('40'))
        # Centro: 2 estuches + examen = 130, anticipo 100 por QR (saldo 30).
        servicios.registrar_venta(self.cajero, [(self.estuche, 2), (self.examen, 1)], Decimal('100'), 'QR',
                                  cliente_nombre='Beto')
        # Norte: armazón 300 con tarjeta.
        servicios.registrar_venta(self.cajero_norte, [(self.armazon, 1)], Decimal('300'), 'TARJETA', cliente_nombre='Ciro')
        # Una venta anulada: no suma en los totales ni en los productos.
        anulada = servicios.registrar_venta(self.cajero, [(self.armazon, 2)], Decimal('600'), 'EFECTIVO',
                                            cliente_nombre='Dina')
        servicios.anular_venta(anulada, self.gerente, 'Desistió')
        self.hoy = timezone.localdate()

    def test_resumen(self):
        datos = reportes.resumen(self.hoy, self.hoy)
        self.assertEqual((datos['cantidad'], datos['total'], datos['descuentos']), (3, Decimal('730'), Decimal('40')))
        self.assertEqual((datos['saldo'], datos['ticket_promedio']), (Decimal('30'), Decimal('243.33')))
        self.assertEqual(dict(datos['cobros']), {'Efectivo': Decimal('300'), 'QR': Decimal('100'), 'Tarjeta': Decimal('300')})
        self.assertEqual(datos['cobrado'], Decimal('700'))
        self.assertEqual((datos['anuladas']['cantidad'], datos['anuladas']['total']), (1, Decimal('600')))
        self.assertEqual([(d['cantidad'], d['total'], d['porcentaje']) for d in datos['dias']], [(3, Decimal('730'), 100)])
        # Por sucursal y fuera del período.
        self.assertEqual(reportes.resumen(self.hoy, self.hoy, sucursal=self.norte)['total'], Decimal('300'))
        self.assertEqual(reportes.resumen(self.hoy - timedelta(days=5), self.hoy - timedelta(days=1))['cantidad'], 0)

    def test_por_vendedor_y_por_producto(self):
        vendedores = reportes.por_vendedor(self.hoy, self.hoy)
        self.assertEqual([(f['vendedor'], f['cantidad'], f['total'], f['saldo']) for f in vendedores],
                         [(self.cajero, 2, Decimal('430'), Decimal('30')), (self.cajero_norte, 1, Decimal('300'), Decimal('0'))])
        filas, sin_detalle = reportes.por_producto(self.hoy, self.hoy)
        productos = {f['articulo__codigo']: f for f in filas}
        self.assertEqual((productos['ARM-1']['unidades'], productos['ARM-1']['importe'], productos['ARM-1']['costo']),
                         (2, Decimal('600.00'), Decimal('240.00')))
        self.assertEqual((productos['ACC-1']['unidades'], productos['ACC-1']['margen']), (3, Decimal('90.00')))
        self.assertEqual(productos['SRV-1']['margen_porcentaje'], Decimal('100.0'))
        self.assertEqual(sin_detalle, 0)
        solo_norte, _ = reportes.por_producto(self.hoy, self.hoy, vendedor=self.cajero_norte)
        self.assertEqual([f['articulo__codigo'] for f in solo_norte], ['ARM-1'])

    def test_pantalla_csv_y_permisos(self):
        url = reverse('venta_reporte')
        self.client.force_login(self.gerente)
        for vista in ('resumen', 'vendedores', 'productos'):
            with self.subTest(vista=vista):
                self.assertEqual(self.client.get(url, {'vista': vista}).status_code, 200)
        filtro = {'desde': f'{self.hoy:%Y-%m-%d}', 'hasta': f'{self.hoy:%Y-%m-%d}', 'sucursal': self.sucursal.pk}
        pagina = self.client.get(url, {**filtro, 'vista': 'vendedores'})
        self.assertEqual([f['vendedor'] for f in pagina.context['filas']], [self.cajero])
        csv = self.client.get(url, {**filtro, 'vista': 'productos', 'formato': 'csv'}).content.decode('utf-8-sig')
        self.assertTrue(csv.startswith('Código;Artículo;Categoría;Unidades;Importe (Bs);Costo (Bs)'))
        self.assertIn('ACC-1;Estuche;Ópticos;3;120,00;30,00;90,00;75,0', csv)
        invertido = self.client.get(url, {**filtro, 'desde': f'{self.hoy + timedelta(days=1):%Y-%m-%d}'})
        self.assertContains(invertido, 'posterior')
        # Un vendedor no ve los reportes de todos.
        self.client.force_login(self.cajero)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_venta_sin_detalle_se_informa(self):
        Venta.objects.create(vendedor=self.cajero, sucursal=self.sucursal, cliente_nombre='Antigua',
                             descripcion='Lentes', total=Decimal('100'))
        self.assertEqual(reportes.por_producto(self.hoy, self.hoy)[1], 1)

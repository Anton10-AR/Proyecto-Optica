from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.urls import reverse

from caja.models import MovimientoCaja
from caja.servicios import abrir_caja
from core import roles
from core.tests import BaseTest, crear_usuario
from inventario import servicios as inventario
from inventario.models import Articulo, Categoria, Existencia, Movimiento, Proveedor
from ventas import servicios
from ventas.models import Venta


class VentaTests(BaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.gerente = crear_usuario('gerente', roles.GERENTE, cls.sucursal, ci='6666666')
        categoria = Categoria.objects.create(nombre='Armazones')
        cls.armazon = Articulo.objects.create(codigo='ARM-1', nombre='Armazón', categoria=categoria,
                                              precio_venta=Decimal('300'))
        cls.estuche = Articulo.objects.create(codigo='ACC-1', nombre='Estuche', categoria=categoria,
                                              precio_venta=Decimal('40'))
        cls.examen = Articulo.objects.create(codigo='SRV-1', nombre='Examen visual', categoria=categoria,
                                             precio_venta=Decimal('50'), controla_stock=False)
        cls.almacen = crear_usuario('almacen', roles.ALMACEN, cls.sucursal, ci='4444444')
        inventario.registrar_ingreso(cls.almacen, cls.sucursal, Proveedor.objects.create(razon_social='Andina'), [
            (cls.armazon, 5, Decimal('120')), (cls.estuche, 10, Decimal('10'))])

    def stock(self, articulo):
        return Existencia.objects.get(articulo=articulo, sucursal=self.sucursal).cantidad

    def registrar(self, lineas=None, **cambios):
        datos = dict(cliente_nombre='Cliente', cliente_ci='', monto_pago=Decimal('200'), forma_pago='EFECTIVO')
        datos.update(cambios)
        return servicios.registrar_venta(self.cajero, lineas=lineas or [(self.armazon, 1), (self.examen, 1)], **datos)

    # ---------- Registro ----------

    def test_venta_requiere_caja_abierta(self):
        with self.assertRaises(ValidationError):
            self.registrar()

    def test_venta_registra_al_vendedor_y_el_pago_en_caja(self):
        sesion = abrir_caja(self.cajero, Decimal('100'))
        venta = self.registrar()
        self.assertEqual((venta.vendedor, venta.sucursal), (self.cajero, self.sucursal))
        pago = venta.pagos.get()
        self.assertEqual(pago.movimiento_caja.sesion, sesion)
        self.assertEqual(venta.total, Decimal('350'))  # 300 del armazón + 50 del examen
        self.assertEqual(venta.saldo, Decimal('150'))
        self.assertEqual(sesion.efectivo_esperado, Decimal('300'))

    def test_venta_descuenta_stock_y_registra_el_kardex(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar([(self.armazon, 2), (self.estuche, 3), (self.examen, 1)])
        self.assertEqual((self.stock(self.armazon), self.stock(self.estuche)), (3, 7))
        movimiento = Movimiento.objects.get(articulo=self.armazon, tipo=Movimiento.Tipo.VENTA)
        self.assertEqual((movimiento.cantidad, movimiento.saldo, movimiento.referencia),
                         (2, 3, f'Nota de venta {venta.numero}'))
        self.assertEqual(movimiento.costo_unitario, Decimal('120'))
        # El servicio se vende pero no tiene stock ni kardex.
        self.assertFalse(Movimiento.objects.filter(articulo=self.examen).exists())
        detalle = venta.detalles.get(articulo=self.armazon)
        self.assertEqual((detalle.precio_unitario, detalle.costo_unitario), (Decimal('300'), Decimal('120')))

    def test_sin_stock_no_se_registra_nada(self):
        sesion = abrir_caja(self.cajero, Decimal('0'))
        with self.assertRaisesMessage(ValidationError, 'Stock insuficiente de ARM-1'):
            self.registrar([(self.estuche, 2), (self.armazon, 6)])
        self.assertFalse(Venta.objects.exists())
        self.assertFalse(sesion.movimientos.exists())
        self.assertEqual((self.stock(self.armazon), self.stock(self.estuche)), (5, 10))

    def test_descuento_y_validaciones_del_total(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar([(self.armazon, 1), (self.estuche, 1)], descuento=Decimal('40'),
                               monto_pago=Decimal('300'))
        self.assertEqual((venta.subtotal, venta.total, venta.saldo), (Decimal('340'), Decimal('300'), Decimal('0')))
        with self.assertRaisesMessage(ValidationError, 'menor que el subtotal'):
            self.registrar([(self.estuche, 1)], descuento=Decimal('40'))
        with self.assertRaisesMessage(ValidationError, 'no puede superar el total'):
            self.registrar([(self.estuche, 1)], monto_pago=Decimal('41'))
        with self.assertRaisesMessage(ValidationError, 'repetido'):
            self.registrar([(self.estuche, 1), (self.estuche, 2)])
        self.estuche.activo = False
        self.estuche.save()
        with self.assertRaisesMessage(ValidationError, 'inactivo'):
            self.registrar([(self.estuche, 1)], monto_pago=Decimal('10'))

    def test_pago_no_puede_superar_el_saldo(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar()
        with self.assertRaises(ValidationError):
            servicios.registrar_pago(venta, self.cajero, Decimal('151'), 'QR')
        servicios.registrar_pago(venta, self.cajero, Decimal('150'), 'QR')
        self.assertEqual(venta.saldo, Decimal('0'))

    def test_no_se_puede_borrar_un_vendedor_con_ventas(self):
        abrir_caja(self.cajero, Decimal('0'))
        self.registrar()
        with self.assertRaises(ProtectedError):
            self.cajero.delete()

    def test_mensaje_de_saldo_usa_formato_local(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar([(self.armazon, 5)], monto_pago=Decimal('700'))
        with self.assertRaisesMessage(ValidationError, 'saldo pendiente (Bs 800,00)'):
            servicios.registrar_pago(venta, self.cajero, Decimal('900'), 'QR')

    # ---------- Vistas ----------

    def test_vista_crear_y_nota_de_venta_muestra_al_vendedor(self):
        self.client.force_login(self.cajero)
        self.assertRedirects(self.client.get(reverse('venta_crear')), reverse('mi_caja'))
        abrir_caja(self.cajero, Decimal('0'))
        formulario = self.client.get(reverse('venta_crear'))
        self.assertContains(formulario, 'ARM-1 · Armazón · Bs 300,00 · stock 5')
        respuesta = self.client.post(reverse('venta_crear'), {
            'cliente_nombre': 'Ana', 'descuento': '20', 'monto_pago': '320', 'forma_pago': 'TARJETA',
            'lineas-TOTAL_FORMS': '5', 'lineas-INITIAL_FORMS': '0',
            'lineas-0-articulo': self.armazon.pk, 'lineas-0-cantidad': '1',
            'lineas-1-articulo': self.estuche.pk, 'lineas-1-cantidad': '1'})
        venta = Venta.objects.get()
        self.assertRedirects(respuesta, reverse('venta_detalle', args=[venta.pk]))
        self.assertEqual(venta.total, Decimal('320'))
        nota = self.client.get(reverse('venta_nota', args=[venta.pk]))
        self.assertContains(nota, f'(ID {self.cajero.pk})')
        self.assertContains(nota, 'Estuche')

    def test_vista_muestra_el_error_de_stock(self):
        self.client.force_login(self.cajero)
        abrir_caja(self.cajero, Decimal('0'))
        respuesta = self.client.post(reverse('venta_crear'), {
            'cliente_nombre': 'Ana', 'monto_pago': '100', 'forma_pago': 'EFECTIVO',
            'lineas-TOTAL_FORMS': '5', 'lineas-INITIAL_FORMS': '0',
            'lineas-0-articulo': self.armazon.pk, 'lineas-0-cantidad': '9'})
        self.assertContains(respuesta, 'Stock insuficiente')
        self.assertFalse(Venta.objects.exists())

    def test_un_vendedor_no_ve_ventas_ajenas(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar()
        otro = crear_usuario('cajero2', roles.CAJERO_VENDEDOR, self.sucursal, ci='8888888')
        self.client.force_login(otro)
        self.assertEqual(self.client.get(reverse('venta_detalle', args=[venta.pk])).status_code, 403)
        self.assertEqual(len(self.client.get(reverse('venta_lista')).context['pagina']), 0)

    # ---------- Anulación ----------

    def test_anular_repone_stock_y_devuelve_lo_pagado(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar([(self.armazon, 2), (self.examen, 1)], monto_pago=Decimal('400'))
        servicios.registrar_pago(venta, self.cajero, Decimal('100'), 'QR')
        caja_gerente = abrir_caja(self.gerente, Decimal('500'))
        servicios.anular_venta(venta, self.gerente, 'El cliente desistió')
        venta.refresh_from_db()
        self.assertEqual((venta.estado, venta.usuario_anulacion), (Venta.Estado.ANULADA, self.gerente))
        self.assertEqual(self.stock(self.armazon), 5)
        reposicion = Movimiento.objects.get(tipo=Movimiento.Tipo.ANULACION_VENTA)
        self.assertEqual((reposicion.cantidad, reposicion.costo_unitario), (2, Decimal('120')))
        devoluciones = caja_gerente.movimientos.filter(tipo=MovimientoCaja.Tipo.EGRESO)
        self.assertEqual(sorted(devoluciones.values_list('forma_pago', 'monto')),
                         [('EFECTIVO', Decimal('400')), ('QR', Decimal('100'))])
        self.assertEqual(caja_gerente.efectivo_esperado, Decimal('100'))
        with self.assertRaisesMessage(ValidationError, 'ya está anulada'):
            servicios.anular_venta(venta, self.gerente, 'Otra vez')
        with self.assertRaisesMessage(ValidationError, 'anulada'):
            servicios.registrar_pago(venta, self.cajero, Decimal('1'), 'QR')

    def test_anular_repone_al_costo_de_la_venta(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar([(self.armazon, 4)], monto_pago=Decimal('1'))
        # Después de vender, se compra más caro: 1 unidad a 120 + 1 a 180 → promedio 150.
        inventario.registrar_ingreso(self.almacen, self.sucursal, Proveedor.objects.get(), [(self.armazon, 1, Decimal('180'))])
        self.armazon.refresh_from_db()
        self.assertEqual(self.armazon.costo_promedio, Decimal('150'))
        abrir_caja(self.gerente, Decimal('10'))
        servicios.anular_venta(venta, self.gerente, 'Error de registro')
        self.armazon.refresh_from_db()
        # Vuelven 4 unidades a 120: (2 × 150 + 4 × 120) / 6 = 130.
        self.assertEqual(self.armazon.costo_promedio, Decimal('130'))

    def test_anular_exige_motivo_y_caja_si_hay_pagos(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar()
        with self.assertRaisesMessage(ValidationError, 'motivo'):
            servicios.anular_venta(venta, self.gerente, '  ')
        with self.assertRaisesMessage(ValidationError, 'Abra su caja'):
            servicios.anular_venta(venta, self.gerente, 'Desistió')
        self.assertEqual(self.stock(self.armazon), 4)
        abrir_caja(self.gerente, Decimal('100'))
        with self.assertRaisesMessage(ValidationError, 'supera el efectivo'):
            servicios.anular_venta(venta, self.gerente, 'Desistió')  # devuelve 200 y solo hay 100
        venta.refresh_from_db()
        self.assertEqual((venta.estado, self.stock(self.armazon)), (Venta.Estado.VIGENTE, 4))

    def test_vista_anular_y_permisos(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar()
        url = reverse('venta_anular', args=[venta.pk])
        self.client.force_login(self.cajero)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertNotContains(self.client.get(reverse('venta_detalle', args=[venta.pk])), url)
        self.client.force_login(self.gerente)
        self.assertContains(self.client.get(reverse('venta_detalle', args=[venta.pk])), url)
        self.assertContains(self.client.get(url), 'Abra su caja')
        abrir_caja(self.gerente, Decimal('500'))
        respuesta = self.client.post(url, {'motivo': 'El cliente desistió'})
        self.assertRedirects(respuesta, reverse('venta_detalle', args=[venta.pk]))
        self.assertContains(self.client.get(reverse('venta_detalle', args=[venta.pk])), 'El cliente desistió')

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.urls import reverse

from caja import servicios
from caja.models import FormaPago, MovimientoCaja, SesionCaja
from core import roles
from core.tests import BaseTest, crear_usuario


class CajaTests(BaseTest):
    def test_abrir_caja_vincula_al_usuario_y_su_sucursal(self):
        sesion = servicios.abrir_caja(self.cajero, Decimal('100'))
        self.assertEqual((sesion.usuario, sesion.sucursal), (self.cajero, self.sucursal))

    def test_solo_una_caja_abierta_por_usuario(self):
        servicios.abrir_caja(self.cajero, Decimal('100'))
        with self.assertRaises(ValidationError):
            servicios.abrir_caja(self.cajero, Decimal('50'))

    def test_requiere_sucursal(self):
        sin_sucursal = crear_usuario('sinsucursal', roles.CAJERO_VENDEDOR, None, ci='9999999')
        with self.assertRaises(ValidationError):
            servicios.abrir_caja(sin_sucursal, Decimal('100'))

    def test_movimiento_sin_caja_abierta_falla(self):
        with self.assertRaises(ValidationError):
            servicios.registrar_movimiento(self.cajero, MovimientoCaja.Tipo.INGRESO, FormaPago.EFECTIVO,
                                           Decimal('10'), 'x')

    def test_egreso_no_puede_superar_el_efectivo(self):
        servicios.abrir_caja(self.cajero, Decimal('100'))
        with self.assertRaises(ValidationError):
            servicios.registrar_movimiento(self.cajero, MovimientoCaja.Tipo.EGRESO, FormaPago.EFECTIVO,
                                           Decimal('150'), 'Compra')

    def test_arqueo_calcula_esperado_y_diferencia(self):
        servicios.abrir_caja(self.cajero, Decimal('100'))
        servicios.registrar_movimiento(self.cajero, 'INGRESO', 'EFECTIVO', Decimal('50'), 'Venta')
        servicios.registrar_movimiento(self.cajero, 'INGRESO', 'QR', Decimal('80'), 'Venta QR')
        servicios.registrar_movimiento(self.cajero, 'EGRESO', 'EFECTIVO', Decimal('20'), 'Taxi')
        sesion = servicios.cerrar_caja(self.cajero, Decimal('125'))
        self.assertEqual(sesion.estado, SesionCaja.Estado.CERRADA)
        self.assertEqual(sesion.monto_esperado, Decimal('130'))  # 100 + 50 - 20; el QR no es efectivo
        self.assertEqual(sesion.diferencia, Decimal('-5'))
        self.assertIsNone(servicios.caja_abierta(self.cajero))

    def test_vistas_de_caja(self):
        self.client.force_login(self.cajero)
        self.client.post(reverse('caja_abrir'), {'monto_inicial': '100'})
        sesion = servicios.caja_abierta(self.cajero)
        self.assertIsNotNone(sesion)
        self.client.post(reverse('caja_movimiento'), {
            'tipo': 'INGRESO', 'forma_pago': 'EFECTIVO', 'monto': '30', 'concepto': 'Ajuste'})
        self.assertEqual(sesion.movimientos.get().usuario, self.cajero)
        self.client.post(reverse('caja_cerrar'), {'monto_contado': '130'})
        sesion.refresh_from_db()
        self.assertEqual(sesion.diferencia, Decimal('0'))

    def test_detalle_de_caja_ajena_requiere_permiso(self):
        sesion = servicios.abrir_caja(self.cajero, Decimal('100'))
        otro = crear_usuario('cajero2', roles.CAJERO_VENDEDOR, self.sucursal, ci='8888888')
        self.client.force_login(otro)
        self.assertEqual(self.client.get(reverse('caja_detalle', args=[sesion.pk])).status_code, 403)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('caja_detalle', args=[sesion.pk])).status_code, 200)

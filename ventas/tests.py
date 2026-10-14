from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.urls import reverse

from caja.servicios import abrir_caja
from core import roles
from core.tests import BaseTest, crear_usuario
from ventas import servicios
from ventas.models import Venta


class VentaTests(BaseTest):
    def registrar(self, **cambios):
        datos = dict(cliente_nombre='Cliente', cliente_ci='', descripcion='Lentes', total=Decimal('500'),
                     monto_pago=Decimal('200'), forma_pago='EFECTIVO')
        datos.update(cambios)
        return servicios.registrar_venta(self.cajero, **datos)

    def test_venta_requiere_caja_abierta(self):
        with self.assertRaises(ValidationError):
            self.registrar()

    def test_venta_registra_al_vendedor_y_el_pago_en_caja(self):
        sesion = abrir_caja(self.cajero, Decimal('100'))
        venta = self.registrar()
        self.assertEqual((venta.vendedor, venta.sucursal), (self.cajero, self.sucursal))
        pago = venta.pagos.get()
        self.assertEqual(pago.movimiento_caja.sesion, sesion)
        self.assertEqual(venta.saldo, Decimal('300'))
        self.assertEqual(sesion.efectivo_esperado, Decimal('300'))

    def test_pago_no_puede_superar_el_saldo(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar()
        with self.assertRaises(ValidationError):
            servicios.registrar_pago(venta, self.cajero, Decimal('301'), 'QR')
        servicios.registrar_pago(venta, self.cajero, Decimal('300'), 'QR')
        self.assertEqual(venta.saldo, Decimal('0'))

    def test_no_se_puede_borrar_un_vendedor_con_ventas(self):
        abrir_caja(self.cajero, Decimal('0'))
        self.registrar()
        with self.assertRaises(ProtectedError):
            self.cajero.delete()

    def test_vista_crear_y_nota_de_venta_muestra_al_vendedor(self):
        self.client.force_login(self.cajero)
        self.assertRedirects(self.client.get(reverse('venta_crear')), reverse('mi_caja'))
        abrir_caja(self.cajero, Decimal('0'))
        respuesta = self.client.post(reverse('venta_crear'), {
            'cliente_nombre': 'Ana', 'descripcion': 'Armazón', 'total': '300',
            'monto_pago': '300', 'forma_pago': 'TARJETA'})
        venta = Venta.objects.get()
        self.assertRedirects(respuesta, reverse('venta_detalle', args=[venta.pk]))
        nota = self.client.get(reverse('venta_nota', args=[venta.pk]))
        self.assertContains(nota, f'(ID {self.cajero.pk})')

    def test_un_vendedor_no_ve_ventas_ajenas(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar()
        otro = crear_usuario('cajero2', roles.CAJERO_VENDEDOR, self.sucursal, ci='8888888')
        self.client.force_login(otro)
        self.assertEqual(self.client.get(reverse('venta_detalle', args=[venta.pk])).status_code, 403)
        self.assertEqual(len(self.client.get(reverse('venta_lista')).context['pagina']), 0)

    def test_mensaje_de_saldo_usa_formato_local(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.registrar(total=Decimal('1450'), monto_pago=Decimal('700'))
        with self.assertRaisesMessage(ValidationError, 'saldo pendiente (Bs 750,00)'):
            servicios.registrar_pago(venta, self.cajero, Decimal('800'), 'QR')

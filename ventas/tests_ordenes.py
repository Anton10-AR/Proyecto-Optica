"""Clientes, recetas, órdenes de trabajo y anticipo mínimo (RF05, RF21–RF24, RF31, RF32)."""

from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from caja.servicios import abrir_caja
from core import roles
from core.models import Configuracion
from core.tests import BaseTest, crear_usuario
from inventario import servicios as inventario
from inventario.models import Articulo, Categoria, Proveedor
from ventas import servicios
from ventas.forms import RecetaForm
from ventas.models import Cliente, EventoOrden, OrdenTrabajo, Receta, Venta

GRADUACION = {'od_esfera': '-1.25', 'od_cilindro': '-0.50', 'od_eje': '180',
              'oi_esfera': '-1.00', 'oi_cilindro': '0', 'distancia_pupilar': '62'}


class OrdenesTests(BaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.gerente = crear_usuario('gerente', roles.GERENTE, cls.sucursal, ci='6666666')
        cls.optico = crear_usuario('optico', roles.OPTICO, cls.sucursal, ci='7777777')
        almacen = crear_usuario('almacen', roles.ALMACEN, cls.sucursal, ci='4444444')
        categoria = Categoria.objects.create(nombre='Ópticos')
        cls.armazon = Articulo.objects.create(codigo='ARM-1', nombre='Armazón', categoria=categoria,
                                              precio_venta=Decimal('300'))
        cls.luna = Articulo.objects.create(codigo='LUN-1', nombre='Luna monofocal', categoria=categoria,
                                           precio_venta=Decimal('100'), requiere_receta=True)
        cls.liquido = Articulo.objects.create(codigo='ACC-1', nombre='Líquido', categoria=categoria,
                                              precio_venta=Decimal('25'))
        inventario.registrar_ingreso(almacen, cls.sucursal, Proveedor.objects.create(razon_social='Andina'), [
            (cls.armazon, 5, Decimal('120')), (cls.luna, 10, Decimal('40')), (cls.liquido, 10, Decimal('8'))])
        cls.cliente = Cliente.objects.create(nombre='María López', ci_nit='5555555')
        cls.otro = Cliente.objects.create(nombre='Carlos Vargas', ci_nit='6666601')
        cls.receta = Receta.objects.create(
            cliente=cls.cliente, origen=Receta.Origen.EXAMEN, optico=cls.optico, od_esfera=Decimal('-1.25'),
            oi_esfera=Decimal('-1'), distancia_pupilar=Decimal('62'), registrado_por=cls.optico)

    def vender(self, lineas=None, monto=Decimal('300'), **datos):
        datos.setdefault('cliente', self.cliente)
        datos.setdefault('receta', self.receta)
        return servicios.registrar_venta(self.cajero, lineas or [(self.armazon, 1), (self.luna, 2)], monto,
                                         'EFECTIVO', **datos)

    # ---------- Recetas ----------

    def receta_form(self, **cambios):
        datos = {'fecha': timezone.localdate().isoformat(), 'origen': 'EXAMEN', 'optico': self.optico.pk,
                 **GRADUACION, **cambios}
        return RecetaForm(datos, cliente=self.cliente, usuario=self.cajero)

    def test_receta_valida_la_graduacion(self):
        self.assertTrue(self.receta_form().is_valid())
        casos = {
            'od_esfera': ({'od_esfera': '-1.30'}, 'pasos de 0,25'),
            'od_eje': ({'od_eje': ''}, 'indique el eje'),
            'oi_eje': ({'oi_eje': '90'}, 'deje el eje vacío'),
            'od_adicion': ({'od_adicion': '5'}, '+4,00'),
            'distancia_pupilar': ({'distancia_pupilar': '30'}, '40'),
            'fecha': ({'fecha': (timezone.localdate() + timedelta(days=1)).isoformat()}, 'futura'),
        }
        for campo, (cambio, mensaje) in casos.items():
            with self.subTest(campo=campo):
                form = self.receta_form(**cambio)
                self.assertFalse(form.is_valid())
                self.assertIn(mensaje, ' '.join(form.errors[campo]))

    def test_origen_de_la_receta(self):
        # Solo quien realiza exámenes puede figurar como óptico responsable.
        form = self.receta_form(optico=self.cajero.pk)
        self.assertFalse(form.is_valid())
        self.assertIn('optico', form.errors)
        # En una receta externa se exige el médico y se descarta el óptico que quedó elegido en la pantalla.
        self.assertIn('medico', self.receta_form(origen='EXTERNA').errors)
        form = self.receta_form(origen='EXTERNA', medico='Dr. Salinas')
        self.assertTrue(form.is_valid(), form.errors)
        receta = form.save()
        self.assertEqual((receta.optico, receta.registrado_por, receta.responsable), (None, self.cajero, 'Dr. Salinas'))

    def test_vistas_de_clientes_y_recetas(self):
        self.client.force_login(self.optico)
        respuesta = self.client.post(reverse('cliente_crear'), {'nombre': '  Rosa   Quiroga ', 'ci_nit': '7777702'})
        rosa = Cliente.objects.get(ci_nit='7777702')
        self.assertRedirects(respuesta, reverse('cliente_detalle', args=[rosa.pk]))
        self.assertEqual(rosa.nombre, 'Rosa Quiroga')
        repetido = self.client.post(reverse('cliente_crear'), {'nombre': 'Otra', 'ci_nit': '7777702'})
        self.assertContains(repetido, 'Ya hay un cliente con este CI/NIT')
        url = reverse('receta_crear', args=[rosa.pk])
        self.assertRedirects(self.client.post(url, {'fecha': timezone.localdate().isoformat(), 'origen': 'EXAMEN',
                                                    'optico': self.optico.pk, **GRADUACION}),
                             reverse('cliente_detalle', args=[rosa.pk]))
        detalle = self.client.get(reverse('cliente_detalle', args=[rosa.pk]))
        self.assertContains(detalle, '−1,25')  # la graduación se muestra con signo
        self.assertContains(self.client.get(reverse('cliente_lista'), {'q': 'quiroga'}), 'Rosa Quiroga')
        # El empleado no ve clientes; el almacén tampoco.
        self.client.force_login(self.empleado)
        self.assertEqual(self.client.get(reverse('cliente_lista')).status_code, 403)
        self.assertEqual(self.client.get(url).status_code, 403)

    # ---------- Venta de lentes graduados ----------

    def test_venta_con_lentes_genera_la_orden(self):
        abrir_caja(self.cajero, Decimal('0'))
        venta = self.vender(fecha_prometida=timezone.localdate() + timedelta(days=3))
        orden = venta.orden
        self.assertEqual((orden.estado, orden.receta, venta.cliente, venta.cliente_nombre),
                         (OrdenTrabajo.Estado.PENDIENTE, self.receta, self.cliente, 'María López'))
        self.assertEqual(orden.eventos.get().usuario, self.cajero)
        # Una venta sin lentes graduados no genera orden y admite un cliente ocasional.
        simple = servicios.registrar_venta(self.cajero, [(self.liquido, 1)], Decimal('25'), 'QR', cliente_nombre='Ana')
        self.assertFalse(OrdenTrabajo.objects.filter(venta=simple).exists())
        self.assertIsNone(simple.cliente)

    def test_lentes_exigen_cliente_receta_propia_y_anticipo(self):
        abrir_caja(self.cajero, Decimal('0'))
        with self.assertRaisesMessage(ValidationError, 'cliente registrado'):
            self.vender(cliente=None, receta=None, cliente_nombre='Ana')
        with self.assertRaisesMessage(ValidationError, 'Elija la receta'):
            self.vender(receta=None)
        with self.assertRaisesMessage(ValidationError, 'no es de Carlos Vargas'):
            self.vender(cliente=self.otro)
        # Total 500: con el 50 % por defecto, el anticipo mínimo es 250.
        with self.assertRaisesMessage(ValidationError, 'al menos el 50 % del total: Bs 250,00'):
            self.vender(monto=Decimal('249.99'))
        self.assertFalse(Venta.objects.exists())
        configuracion = Configuracion.actual()
        configuracion.anticipo_minimo_porcentaje = 30
        configuracion.save()
        self.assertEqual(self.vender(monto=Decimal('150')).orden.estado, OrdenTrabajo.Estado.PENDIENTE)

    def test_vista_de_venta_con_cliente_y_receta(self):
        abrir_caja(self.cajero, Decimal('0'))
        self.client.force_login(self.cajero)
        formulario = self.client.get(reverse('venta_crear'), {'cliente': self.cliente.pk})
        self.assertEqual(formulario.context['form'].initial['receta'], self.receta.pk)
        opciones = self.client.get(reverse('venta_recetas'), {'cliente': self.cliente.pk})
        self.assertContains(opciones, f'value="{self.receta.pk}" selected')
        respuesta = self.client.post(reverse('venta_crear'), {
            'cliente': self.cliente.pk, 'receta': self.receta.pk, 'descuento': '0', 'monto_pago': '250',
            'forma_pago': 'EFECTIVO', 'lineas-TOTAL_FORMS': '5', 'lineas-INITIAL_FORMS': '0',
            'lineas-0-articulo': self.armazon.pk, 'lineas-0-cantidad': '1',
            'lineas-1-articulo': self.luna.pk, 'lineas-1-cantidad': '2'})
        venta = Venta.objects.get()
        self.assertRedirects(respuesta, reverse('venta_detalle', args=[venta.pk]))
        self.assertContains(self.client.get(reverse('venta_nota', args=[venta.pk])), f'N.º {venta.orden.numero}')
        # Sin cliente registrado ni nombre, el formulario lo pide.
        sin_cliente = self.client.post(reverse('venta_crear'), {
            'monto_pago': '25', 'forma_pago': 'EFECTIVO', 'lineas-TOTAL_FORMS': '5', 'lineas-INITIAL_FORMS': '0',
            'lineas-0-articulo': self.liquido.pk, 'lineas-0-cantidad': '1'})
        self.assertContains(sin_cliente, 'Elija un cliente registrado o escriba el nombre')

    # ---------- Flujo de la orden y entrega con saldo ----------

    def test_flujo_del_taller(self):
        abrir_caja(self.cajero, Decimal('0'))
        orden = self.vender(monto=Decimal('500')).orden
        with self.assertRaisesMessage(ValidationError, 'Solo se entrega un trabajo listo'):
            servicios.entregar_orden(orden, self.cajero)
        servicios.avanzar_orden(orden, self.optico)
        orden = servicios.avanzar_orden(orden, self.optico, 'Montado')
        self.assertEqual(orden.estado, OrdenTrabajo.Estado.LISTO)
        with self.assertRaisesMessage(ValidationError, 'ya no la modifica'):
            servicios.avanzar_orden(orden, self.optico)
        orden = servicios.entregar_orden(orden, self.cajero)  # venta pagada: se entrega sin autorización
        self.assertEqual(list(orden.eventos.values_list('estado', flat=True)),
                         ['PENDIENTE', 'EN_TALLER', 'LISTO', 'ENTREGADO'])

    def test_entrega_con_saldo_exige_autorizacion_del_gerente(self):
        abrir_caja(self.cajero, Decimal('0'))
        orden = self.vender().orden  # total 500, pagó 300: saldo 200
        servicios.avanzar_orden(orden, self.optico)
        servicios.avanzar_orden(orden, self.optico)
        with self.assertRaisesMessage(ValidationError, 'saldo pendiente de Bs 200,00'):
            servicios.entregar_orden(orden, self.cajero)
        with self.assertRaisesMessage(ValidationError, 'motivo'):
            servicios.autorizar_entrega(orden, self.gerente, ' ')
        orden = servicios.autorizar_entrega(orden, self.gerente, 'Cliente frecuente')
        self.assertEqual((orden.entrega_autorizada_por, orden.motivo_autorizacion), (self.gerente, 'Cliente frecuente'))
        self.assertIsNotNone(orden.fecha_autorizacion)
        orden = servicios.entregar_orden(orden, self.cajero)
        self.assertEqual(orden.estado, OrdenTrabajo.Estado.ENTREGADO)
        self.assertIn('saldo pendiente de Bs 200,00', orden.eventos.last().nota)

    def test_cobrar_el_saldo_permite_entregar(self):
        abrir_caja(self.cajero, Decimal('0'))
        orden = self.vender().orden
        servicios.avanzar_orden(orden, self.optico)
        servicios.avanzar_orden(orden, self.optico)
        servicios.registrar_pago(orden.venta, self.cajero, Decimal('200'), 'QR')
        # Pagada la venta, ya no hace falta la autorización del gerente.
        with self.assertRaisesMessage(ValidationError, 'no hace falta'):
            servicios.autorizar_entrega(orden, self.gerente, 'Sin saldo')
        self.assertEqual(servicios.entregar_orden(orden, self.cajero).estado, OrdenTrabajo.Estado.ENTREGADO)

    def test_anular_la_venta_anula_la_orden_salvo_si_se_entrego(self):
        abrir_caja(self.cajero, Decimal('0'))
        abrir_caja(self.gerente, Decimal('1000'))
        orden = self.vender().orden
        servicios.anular_venta(orden.venta, self.gerente, 'Desistió')
        orden.refresh_from_db()
        self.assertEqual(orden.estado, OrdenTrabajo.Estado.ANULADA)
        self.assertIn('Desistió', orden.eventos.last().nota)
        entregada = self.vender(monto=Decimal('500')).orden
        servicios.avanzar_orden(entregada, self.optico)
        servicios.avanzar_orden(entregada, self.optico)
        servicios.entregar_orden(entregada, self.cajero)
        with self.assertRaisesMessage(ValidationError, 'ya se entregó'):
            servicios.anular_venta(entregada.venta, self.gerente, 'Desistió')

    def test_vistas_y_permisos_de_las_ordenes(self):
        abrir_caja(self.cajero, Decimal('0'))
        orden = self.vender().orden
        detalle = reverse('orden_detalle', args=[orden.pk])
        # El óptico avanza la orden; el cajero no puede.
        self.client.force_login(self.cajero)
        self.assertEqual(self.client.post(reverse('orden_avanzar', args=[orden.pk])).status_code, 403)
        self.client.force_login(self.optico)
        self.assertContains(self.client.get(detalle), 'Pasar al taller')
        self.assertRedirects(self.client.post(reverse('orden_avanzar', args=[orden.pk])), detalle)
        self.client.post(reverse('orden_avanzar', args=[orden.pk]))
        self.assertEqual(self.client.get(reverse('inicio')).context['ordenes'], {'en_curso': 0, 'listas': 1})
        # Con saldo, el botón de entrega está desactivado; el gerente ve el formulario para autorizar.
        self.assertContains(self.client.get(detalle), 'title="La venta tiene saldo pendiente"')
        self.assertEqual(self.client.post(reverse('orden_autorizar', args=[orden.pk]), {'motivo': 'x'}).status_code, 403)
        self.client.force_login(self.gerente)
        self.assertContains(self.client.get(detalle), 'Autorizar la entrega con saldo')
        self.client.post(reverse('orden_autorizar', args=[orden.pk]), {'motivo': 'Paga el viernes'})
        self.client.force_login(self.cajero)
        self.assertRedirects(self.client.post(reverse('orden_entregar', args=[orden.pk])), detalle)
        orden.refresh_from_db()
        self.assertEqual(orden.estado, OrdenTrabajo.Estado.ENTREGADO)
        listado = self.client.get(reverse('orden_lista'), {'estado': 'ENTREGADO'}).context['pagina']
        self.assertEqual(list(listado), [orden])
        self.client.force_login(self.empleado)
        self.assertEqual(self.client.get(reverse('orden_lista')).status_code, 403)

    def test_cobro_desde_la_orden_vuelve_a_la_orden(self):
        abrir_caja(self.cajero, Decimal('0'))
        orden = self.vender().orden
        otro_cajero = crear_usuario('cajero2', roles.CAJERO_VENDEDOR, self.sucursal, ci='8888888')
        abrir_caja(otro_cajero, Decimal('0'))
        self.client.force_login(otro_cajero)
        respuesta = self.client.post(reverse('venta_cobrar', args=[orden.venta.pk]),
                                     {'monto': '200', 'forma_pago': 'QR', 'desde': 'orden'})
        self.assertRedirects(respuesta, reverse('orden_detalle', args=[orden.pk]))
        self.assertEqual(orden.venta.saldo, Decimal('0'))

    def test_parametros_solo_para_el_gerente(self):
        self.client.force_login(self.cajero)
        self.assertEqual(self.client.get(reverse('parametros')).status_code, 403)
        self.client.force_login(self.gerente)
        self.assertRedirects(self.client.post(reverse('parametros'), {
            'seccion': 'ventas', 'ventas-anticipo_minimo_porcentaje': '40'}), reverse('parametros'))
        self.assertEqual(Configuracion.actual().anticipo_minimo_porcentaje, 40)
        self.assertContains(self.client.post(reverse('parametros'), {
            'seccion': 'ventas', 'ventas-anticipo_minimo_porcentaje': '120'}), '100')
        self.assertEqual(EventoOrden.objects.count(), 0)

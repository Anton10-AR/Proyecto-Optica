from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.urls import reverse

from core import roles
from core.models import Sucursal
from core.tests import BaseTest, crear_usuario
from inventario import servicios
from inventario.forms import ArticuloForm
from inventario.models import Ajuste, Articulo, Categoria, Existencia, Ingreso, Movimiento, Proveedor, Traspaso


class CatalogoTests(BaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.almacen = crear_usuario('almacen', roles.ALMACEN, cls.sucursal, ci='4444444')
        cls.armazones = Categoria.objects.create(nombre='Armazones')
        cls.servicios = Categoria.objects.create(nombre='Servicios')
        cls.articulo = Articulo.objects.create(codigo='ARM-001', codigo_barras='7790001', nombre='Armazón metálico',
                                               categoria=cls.armazones, precio_venta=Decimal('350'), stock_minimo=2)

    def datos_articulo(self, **cambios):
        datos = {'codigo': 'arm-002', 'codigo_barras': '', 'nombre': ' Armazón acetato ', 'categoria': self.armazones.pk,
                 'precio_venta': '280', 'stock_minimo': '1', 'controla_stock': 'on', 'activo': 'on'}
        datos.update(cambios)
        return datos

    def test_almacen_registra_un_articulo_normalizado(self):
        self.client.force_login(self.almacen)
        respuesta = self.client.post(reverse('articulo_crear'), self.datos_articulo())
        articulo = Articulo.objects.get(codigo='ARM-002')
        self.assertRedirects(respuesta, reverse('articulo_detalle', args=[articulo.pk]))
        self.assertEqual((articulo.nombre, articulo.codigo_barras), ('Armazón acetato', None))

    def test_codigo_duplicado_se_rechaza_sin_distinguir_mayusculas(self):
        form = ArticuloForm(self.datos_articulo(codigo='arm-001'))
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)

    def test_varios_articulos_sin_codigo_de_barras(self):
        for codigo in ('ARM-002', 'ARM-003'):
            form = ArticuloForm(self.datos_articulo(codigo=codigo))
            self.assertTrue(form.is_valid(), form.errors)
            form.save()
        self.assertEqual(Articulo.objects.filter(codigo_barras__isnull=True).count(), 2)

    def test_editar_no_crea_otro_articulo(self):
        self.client.force_login(self.almacen)
        self.client.post(reverse('articulo_editar', args=[self.articulo.pk]),
                         self.datos_articulo(codigo='ARM-001', codigo_barras='7790001', precio_venta='400'))
        self.assertEqual(Articulo.objects.count(), 1)
        self.articulo.refresh_from_db()
        self.assertEqual(self.articulo.precio_venta, Decimal('400'))

    def test_cajero_consulta_pero_no_edita_el_catalogo(self):
        self.client.force_login(self.cajero)
        self.assertEqual(self.client.get(reverse('articulo_lista')).status_code, 200)
        self.assertEqual(self.client.get(reverse('articulo_detalle', args=[self.articulo.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('articulo_crear')).status_code, 403)
        self.assertEqual(self.client.get(reverse('categoria_lista')).status_code, 403)
        self.assertEqual(self.client.get(reverse('proveedor_lista')).status_code, 403)

    def test_empleado_no_ve_el_inventario(self):
        self.client.force_login(self.empleado)
        self.assertEqual(self.client.get(reverse('articulo_lista')).status_code, 403)

    def test_busqueda_por_codigo_de_barras_y_stock_total(self):
        norte = Sucursal.objects.create(nombre='Norte', direccion='Calle 2', latitud=0, longitud=0)
        Existencia.objects.create(articulo=self.articulo, sucursal=self.sucursal, cantidad=3)
        Existencia.objects.create(articulo=self.articulo, sucursal=norte, cantidad=4)
        Articulo.objects.create(codigo='ARM-009', nombre='Otro', categoria=self.armazones, precio_venta=1)
        self.client.force_login(self.cajero)
        pagina = self.client.get(reverse('articulo_lista'), {'q': '7790001'}).context['pagina']
        self.assertEqual([(a.codigo, a.stock_total) for a in pagina], [('ARM-001', 7)])

    def test_detalle_lista_todas_las_sucursales_activas(self):
        Sucursal.objects.create(nombre='Norte', direccion='Calle 2', latitud=0, longitud=0)
        self.client.force_login(self.cajero)
        existencias = self.client.get(reverse('articulo_detalle', args=[self.articulo.pk])).context['existencias']
        self.assertEqual([(s.nombre, c) for s, c in existencias], [('Centro', 0), ('Norte', 0)])

    def test_no_deja_de_controlar_stock_si_hay_existencias(self):
        Existencia.objects.create(articulo=self.articulo, sucursal=self.sucursal, cantidad=1)
        datos = self.datos_articulo(codigo='ARM-001', codigo_barras='7790001')
        del datos['controla_stock']
        form = ArticuloForm(datos, instance=self.articulo)
        self.assertFalse(form.is_valid())
        self.assertIn('controla_stock', form.errors)

    def test_existencia_no_puede_ser_negativa(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Existencia.objects.create(articulo=self.articulo, sucursal=self.sucursal, cantidad=-1)

    def test_almacen_registra_proveedor_sin_nit_duplicado(self):
        Proveedor.objects.create(razon_social='Ópticos del Sur SRL', nit='1020304')
        self.client.force_login(self.almacen)
        respuesta = self.client.post(reverse('proveedor_crear'), {'razon_social': 'ópticos del sur srl', 'nit': '1020304',
                                                                   'activo': 'on'})
        form = respuesta.context['form']
        self.assertEqual(set(form.errors), {'razon_social', 'nit'})
        self.client.post(reverse('proveedor_crear'), {'razon_social': 'Lunas Bolivia', 'nit': '', 'activo': 'on'})
        self.assertIsNone(Proveedor.objects.get(razon_social='Lunas Bolivia').nit)

    def test_categoria_inactiva_no_se_ofrece_para_articulos_nuevos(self):
        self.servicios.activa = False
        self.servicios.save()
        self.assertNotIn(self.servicios, ArticuloForm().fields['categoria'].queryset)
        articulo = Articulo.objects.create(codigo='SRV-1', nombre='Examen', categoria=self.servicios,
                                           precio_venta=50, controla_stock=False)
        self.assertIn(self.servicios, ArticuloForm(instance=articulo).fields['categoria'].queryset)


class MovimientosTests(BaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.norte = Sucursal.objects.create(nombre='Norte', direccion='Calle 2', latitud=0, longitud=0)
        cls.almacen = crear_usuario('almacen', roles.ALMACEN, cls.sucursal, ci='4444444')
        cls.cajero_norte = crear_usuario('cajeronorte', roles.CAJERO_VENDEDOR, cls.norte, ci='5555555')
        categoria = Categoria.objects.create(nombre='Armazones')
        cls.proveedor = Proveedor.objects.create(razon_social='Óptica Andina')
        cls.armazon = Articulo.objects.create(codigo='ARM-1', nombre='Armazón', categoria=categoria, precio_venta=300)
        cls.estuche = Articulo.objects.create(codigo='ACC-1', nombre='Estuche', categoria=categoria, precio_venta=30)
        cls.examen = Articulo.objects.create(codigo='SRV-1', nombre='Examen', categoria=categoria, precio_venta=50,
                                             controla_stock=False)

    def stock(self, articulo, sucursal):
        existencia = Existencia.objects.filter(articulo=articulo, sucursal=sucursal).first()
        return existencia.cantidad if existencia else 0

    def comprar(self, cantidad, costo, articulo=None, sucursal=None):
        return servicios.registrar_ingreso(self.almacen, sucursal or self.sucursal, self.proveedor,
                                           [(articulo or self.armazon, cantidad, Decimal(costo))])

    def test_ingreso_recalcula_el_costo_promedio_ponderado(self):
        self.comprar(10, '100')
        self.comprar(5, '130')
        self.armazon.refresh_from_db()
        self.assertEqual(self.armazon.costo_promedio, Decimal('110'))  # (10 x 100 + 5 x 130) / 15
        self.assertEqual(self.stock(self.armazon, self.sucursal), 15)
        kardex = list(Movimiento.objects.filter(articulo=self.armazon).values_list('saldo', 'costo_promedio'))
        self.assertEqual(kardex, [(10, Decimal('100')), (15, Decimal('110'))])

    def test_el_promedio_cuenta_todas_las_sucursales_y_lo_que_esta_en_transito(self):
        self.comprar(10, '100')
        servicios.enviar_traspaso(self.almacen, self.sucursal, self.norte, [(self.armazon, 4)])
        self.comprar(6, '160', sucursal=self.norte)
        self.armazon.refresh_from_db()
        self.assertEqual(self.armazon.costo_promedio, Decimal('122.5'))  # (10 x 100 + 6 x 160) / 16

    def test_sin_stock_suficiente_no_se_aplica_ninguna_linea(self):
        self.comprar(5, '100')
        with self.assertRaisesMessage(ValidationError, 'Stock insuficiente de ACC-1 · Estuche en Centro: hay 0'):
            servicios.enviar_traspaso(self.almacen, self.sucursal, self.norte, [(self.armazon, 3), (self.estuche, 1)])
        self.assertEqual(self.stock(self.armazon, self.sucursal), 5)
        self.assertFalse(Traspaso.objects.exists())
        self.assertEqual(Movimiento.objects.count(), 1)

    def test_traspaso_en_dos_pasos(self):
        self.comprar(10, '100')
        traspaso = servicios.enviar_traspaso(self.almacen, self.sucursal, self.norte, [(self.armazon, 4)])
        self.assertEqual((self.stock(self.armazon, self.sucursal), self.stock(self.armazon, self.norte)), (6, 0))
        self.assertEqual(servicios.unidades_en_transito(self.armazon), 4)
        with self.assertRaisesMessage(ValidationError, 'Solo el personal de Norte'):
            servicios.recibir_traspaso(traspaso, self.cajero)
        servicios.recibir_traspaso(traspaso, self.cajero_norte)
        traspaso.refresh_from_db()
        self.assertEqual((traspaso.estado, traspaso.usuario_recepcion), (Traspaso.Estado.RECIBIDO, self.cajero_norte))
        self.assertEqual(self.stock(self.armazon, self.norte), 4)
        self.assertEqual(servicios.unidades_en_transito(self.armazon), 0)
        with self.assertRaisesMessage(ValidationError, 'ya fue recibido'):
            servicios.recibir_traspaso(traspaso, self.cajero_norte)

    def test_traspaso_a_la_misma_sucursal_se_rechaza(self):
        self.comprar(1, '100')
        with self.assertRaises(ValidationError):
            servicios.enviar_traspaso(self.almacen, self.sucursal, self.sucursal, [(self.armazon, 1)])

    def test_ajustes_exigen_motivo_y_se_valoran_al_costo_promedio(self):
        self.comprar(10, '100')
        with self.assertRaisesMessage(ValidationError, 'motivo'):
            servicios.registrar_ajuste(self.almacen, self.sucursal, self.armazon, Ajuste.Tipo.BAJA, 1, '   ')
        servicios.registrar_ajuste(self.almacen, self.sucursal, self.armazon, Ajuste.Tipo.BAJA, 2, 'Roto')
        servicios.registrar_ajuste(self.almacen, self.sucursal, self.armazon, Ajuste.Tipo.AJUSTE_ENTRADA, 1, 'Conteo')
        with self.assertRaises(ValidationError):
            servicios.registrar_ajuste(self.almacen, self.sucursal, self.armazon, Ajuste.Tipo.AJUSTE_SALIDA, 10, 'Conteo')
        self.assertEqual(self.stock(self.armazon, self.sucursal), 9)
        baja = Movimiento.objects.get(tipo=Movimiento.Tipo.BAJA)
        self.assertEqual((baja.costo_unitario, baja.saldo), (Decimal('100'), 8))

    def test_servicios_e_inactivos_no_ingresan(self):
        with self.assertRaisesMessage(ValidationError, 'no controla stock'):
            self.comprar(1, '10', articulo=self.examen)
        self.estuche.activo = False
        self.estuche.save()
        with self.assertRaisesMessage(ValidationError, 'inactivo'):
            self.comprar(1, '10', articulo=self.estuche)

    def datos_lineas(self, *lineas, **extra):
        datos = {'lineas-TOTAL_FORMS': '5', 'lineas-INITIAL_FORMS': '0', 'lineas-MIN_NUM_FORMS': '0',
                 'lineas-MAX_NUM_FORMS': '1000'}
        for i, linea in enumerate(lineas):
            datos.update({f'lineas-{i}-{campo}': valor for campo, valor in linea.items()})
        datos.update(extra)
        return datos

    def test_vista_registra_un_ingreso_y_rechaza_lineas_repetidas(self):
        self.client.force_login(self.almacen)
        base = {'sucursal': self.sucursal.pk, 'proveedor': self.proveedor.pk, 'documento': 'F-123'}
        linea = {'articulo': self.armazon.pk, 'cantidad': '3', 'costo_unitario': '95.50'}
        respuesta = self.client.post(reverse('ingreso_crear'), self.datos_lineas(linea, linea, **base))
        self.assertIn('repetidos', str(respuesta.context['lineas'].non_form_errors()))
        respuesta = self.client.post(reverse('ingreso_crear'), self.datos_lineas(linea, **base))
        ingreso = Ingreso.objects.get()
        self.assertRedirects(respuesta, reverse('ingreso_detalle', args=[ingreso.pk]))
        self.assertEqual((ingreso.documento, ingreso.total), ('F-123', Decimal('286.5')))
        self.assertEqual(self.stock(self.armazon, self.sucursal), 3)

    def test_vista_muestra_el_error_del_servicio(self):
        self.client.force_login(self.almacen)
        datos = self.datos_lineas({'articulo': self.armazon.pk, 'cantidad': '2'},
                                  origen=self.sucursal.pk, destino=self.norte.pk)
        respuesta = self.client.post(reverse('traspaso_crear'), datos)
        self.assertContains(respuesta, 'Stock insuficiente')
        self.assertFalse(Traspaso.objects.exists())

    def test_permisos_de_movimientos(self):
        self.comprar(5, '100')
        traspaso = servicios.enviar_traspaso(self.almacen, self.sucursal, self.norte, [(self.armazon, 2)])
        self.client.force_login(self.cajero_norte)
        self.assertEqual(self.client.get(reverse('ingreso_crear')).status_code, 403)
        self.assertEqual(self.client.get(reverse('kardex', args=[self.armazon.pk])).status_code, 403)
        self.assertNotContains(self.client.get(reverse('articulo_detalle', args=[self.armazon.pk])), 'Costo promedio')
        self.assertContains(self.client.get(reverse('traspaso_detalle', args=[traspaso.pk])), 'Confirmar recepción')
        self.assertRedirects(self.client.post(reverse('traspaso_recibir', args=[traspaso.pk])),
                             reverse('traspaso_detalle', args=[traspaso.pk]))
        self.assertEqual(self.stock(self.armazon, self.norte), 2)
        self.client.force_login(self.empleado)
        self.assertEqual(self.client.get(reverse('traspaso_lista')).status_code, 403)

    def test_kardex_por_sucursal(self):
        self.comprar(5, '100')
        servicios.enviar_traspaso(self.almacen, self.sucursal, self.norte, [(self.armazon, 2)])
        self.client.force_login(self.almacen)
        url = reverse('kardex', args=[self.armazon.pk])
        pagina = self.client.get(url, {'sucursal': self.sucursal.pk}).context['pagina']
        self.assertEqual([(m.tipo, m.saldo) for m in pagina], [('COMPRA', 5), ('TRASPASO_SALIDA', 3)])
        self.assertEqual(len(self.client.get(url, {'sucursal': self.norte.pk}).context['pagina']), 0)

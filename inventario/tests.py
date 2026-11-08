from decimal import Decimal

from django.db import IntegrityError, transaction
from django.urls import reverse

from core import roles
from core.models import Sucursal
from core.tests import BaseTest, crear_usuario
from inventario.forms import ArticuloForm
from inventario.models import Articulo, Categoria, Existencia, Proveedor


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

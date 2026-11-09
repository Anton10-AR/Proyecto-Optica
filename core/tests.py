from decimal import Decimal
from io import StringIO

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core import roles
from core.models import RegistroActividad, Sucursal, Usuario

CLAVE = 'ClaveSegura2026!'


def crear_usuario(username, rol=None, sucursal=None, **extra):
    datos = {'first_name': username.title(), 'last_name': 'Prueba', 'email': f'{username}@test.bo',
             'ci': extra.pop('ci', None), 'sucursal': sucursal}
    datos.update(extra)
    usuario = Usuario(username=username, rol=Group.objects.get(name=rol) if rol else None, **datos)
    usuario.set_password(CLAVE)
    usuario.save()
    return usuario


class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        roles.configurar_roles()
        cls.sucursal = Sucursal.objects.create(
            nombre='Centro', direccion='Calle 1', latitud=Decimal('-19.0475'), longitud=Decimal('-65.2593'),
        )
        cls.admin = crear_usuario('administrador', roles.ADMINISTRADOR, cls.sucursal, ci='1111111')
        cls.cajero = crear_usuario('cajero', roles.CAJERO_VENDEDOR, cls.sucursal, ci='2222222')
        cls.empleado = crear_usuario('empleado', roles.EMPLEADO, cls.sucursal, ci='3333333')


class SeguridadTests(BaseTest):
    def test_contrasena_se_guarda_con_argon2(self):
        self.assertTrue(self.cajero.password.startswith('argon2'))
        self.assertNotIn(CLAVE, self.cajero.password)

    def test_login_con_usuario_o_correo_sin_distinguir_mayusculas(self):
        for credencial in ('cajero', 'CAJERO', 'cajero@test.bo', 'Cajero@Test.bo'):
            with self.subTest(credencial=credencial):
                self.assertTrue(self.client.login(username=credencial, password=CLAVE))
                self.client.logout()

    def test_usuario_inactivo_no_puede_iniciar_sesion(self):
        self.empleado.is_active = False
        self.empleado.save()
        self.assertFalse(self.client.login(username='empleado', password=CLAVE))

    def test_auditoria_de_inicio_cierre_e_intento_fallido(self):
        self.client.post(reverse('login'), {'username': 'cajero', 'password': 'incorrecta'})
        self.client.post(reverse('login'), {'username': 'cajero', 'password': CLAVE})
        self.client.post(reverse('logout'))
        acciones = list(RegistroActividad.objects.order_by('fecha').values_list('accion', 'credencial'))
        self.assertEqual(acciones, [
            ('INICIO_FALLIDO', 'cajero'), ('INICIO_SESION', ''), ('CIERRE_SESION', ''),
        ])

    def test_sesion_expira_por_inactividad(self):
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
        self.assertEqual(settings.SESSION_ENGINE, 'django.contrib.sessions.backends.db')
        self.assertGreater(settings.SESSION_COOKIE_AGE, 0)

    def test_clave_inicial_obliga_a_cambiarla(self):
        self.empleado.debe_cambiar_clave = True
        self.empleado.save()
        self.client.force_login(self.empleado)
        self.assertRedirects(self.client.get(reverse('asistencia_marcar')), reverse('password_change'))
        respuesta = self.client.post(reverse('password_change'), {
            'old_password': CLAVE, 'new_password1': 'OtraClave2026#', 'new_password2': 'OtraClave2026#',
        })
        self.assertRedirects(respuesta, reverse('inicio'))
        self.empleado.refresh_from_db()
        self.assertFalse(self.empleado.debe_cambiar_clave)
        self.assertTrue(RegistroActividad.objects.filter(accion='CAMBIO_CLAVE', usuario=self.empleado).exists())


class ControlDeAccesoTests(BaseTest):
    def test_rol_se_sincroniza_con_los_grupos(self):
        self.assertEqual(list(self.cajero.groups.values_list('name', flat=True)), [roles.CAJERO_VENDEDOR])
        self.cajero.rol = Group.objects.get(name=roles.EMPLEADO)
        self.cajero.save()
        self.assertEqual(list(self.cajero.groups.values_list('name', flat=True)), [roles.EMPLEADO])

    def test_sin_sesion_todas_las_pantallas_llevan_al_login(self):
        """RF30: también las vistas basadas en clases redirigen al login en lugar de responder 403."""
        for nombre, args in (('usuario_crear', []), ('sucursal_lista', []), ('actividad_lista', []),
                             ('articulo_crear', []), ('categoria_lista', []), ('proveedor_crear', []),
                             ('inicio', []), ('venta_lista', [])):
            with self.subTest(vista=nombre):
                url = reverse(nombre, args=args)
                self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}",
                                     fetch_redirect_response=False)

    def test_restriccion_de_vistas_por_rol(self):
        casos = {
            'usuario_lista': {self.admin: 200, self.cajero: 403, self.empleado: 403},
            'mi_caja': {self.admin: 200, self.cajero: 200, self.empleado: 403},
            'venta_crear': {self.cajero: 302, self.empleado: 403},  # 302: debe abrir caja primero
            'asistencia_marcar': {self.admin: 200, self.cajero: 200, self.empleado: 200},
            'asistencia_todas': {self.admin: 200, self.cajero: 403, self.empleado: 403},
            'actividad_lista': {self.admin: 200, self.cajero: 403},
        }
        for vista, esperados in casos.items():
            for usuario, codigo in esperados.items():
                with self.subTest(vista=vista, usuario=usuario.username):
                    self.client.force_login(usuario)
                    self.assertEqual(self.client.get(reverse(vista)).status_code, codigo)

    def test_anonimo_es_redirigido_al_login(self):
        respuesta = self.client.get(reverse('usuario_lista'))
        self.assertRedirects(respuesta, f"{reverse('login')}?next={reverse('usuario_lista')}")

    def test_menu_se_adapta_al_rol(self):
        self.client.force_login(self.empleado)
        html = self.client.get(reverse('inicio')).content.decode()
        self.assertIn('Marcar entrada/salida', html)
        self.assertNotIn('Administración', html)
        self.assertNotIn('Mi caja', html)


class AdministracionUsuariosTests(BaseTest):
    def datos(self, **cambios):
        datos = {
            'first_name': 'Nuevo', 'last_name': 'Usuario', 'ci': '4444444', 'email': 'nuevo@test.bo',
            'telefono': '71234567', 'username': 'nuevo', 'rol': Group.objects.get(name=roles.EMPLEADO).pk,
            'sucursal': self.sucursal.pk, 'password1': 'Inicial2026!x', 'password2': 'Inicial2026!x',
        }
        datos.update(cambios)
        return datos

    def setUp(self):
        self.client.force_login(self.admin)

    def test_crear_usuario(self):
        respuesta = self.client.post(reverse('usuario_crear'), self.datos())
        self.assertRedirects(respuesta, reverse('usuario_lista'))
        nuevo = Usuario.objects.get(username='nuevo')
        self.assertTrue(nuevo.is_active)
        self.assertTrue(nuevo.debe_cambiar_clave)
        self.assertTrue(nuevo.password.startswith('argon2'))
        self.assertEqual(nuevo.groups.get().name, roles.EMPLEADO)
        registro = RegistroActividad.objects.get(accion='CREACION_USUARIO')
        self.assertEqual((registro.usuario, registro.usuario_afectado), (self.admin, nuevo))

    def test_validaciones_de_formulario(self):
        casos = {
            'correo duplicado (otra capitalización)': ({'email': 'CAJERO@test.bo'}, 'email'),
            'CI duplicado': ({'ci': '2222222'}, 'ci'),
            'usuario duplicado': ({'username': 'Cajero'}, 'username'),
            'correo inválido': ({'email': 'no-es-correo'}, 'email'),
            'CI inválido': ({'ci': '12AB'}, 'ci'),
            'teléfono inválido': ({'telefono': '123'}, 'telefono'),
            'nombre obligatorio': ({'first_name': ''}, 'first_name'),
            'rol obligatorio': ({'rol': ''}, 'rol'),
            'contraseñas distintas': ({'password2': 'Otra2026!x'}, 'password2'),
            'contraseña débil': ({'password1': '12345678', 'password2': '12345678'}, 'password1'),
        }
        for caso, (cambios, campo) in casos.items():
            with self.subTest(caso):
                respuesta = self.client.post(reverse('usuario_crear'), self.datos(**cambios))
                self.assertEqual(respuesta.status_code, 200)
                self.assertIn(campo, respuesta.context['form'].errors)
        self.assertFalse(Usuario.objects.filter(username='nuevo').exists())

    def test_editar_cambia_rol_y_registra_auditoria(self):
        datos = self.datos(username='empleado', email='empleado@test.bo', ci='3333333',
                           rol=Group.objects.get(name=roles.CAJERO_VENDEDOR).pk)
        respuesta = self.client.post(reverse('usuario_editar', args=[self.empleado.pk]), datos)
        self.assertRedirects(respuesta, reverse('usuario_lista'))
        self.empleado.refresh_from_db()
        self.assertEqual(self.empleado.groups.get().name, roles.CAJERO_VENDEDOR)
        self.assertIn('rol', RegistroActividad.objects.get(accion='ACTUALIZACION_USUARIO').detalle)

    def test_resetear_clave(self):
        respuesta = self.client.post(reverse('usuario_resetear_clave', args=[self.empleado.pk]), {
            'new_password1': 'Reseteada2026!', 'new_password2': 'Reseteada2026!',
        })
        self.assertRedirects(respuesta, reverse('usuario_lista'))
        self.empleado.refresh_from_db()
        self.assertTrue(self.empleado.check_password('Reseteada2026!'))
        self.assertTrue(self.empleado.debe_cambiar_clave)
        self.assertTrue(RegistroActividad.objects.filter(accion='RESETEO_CLAVE').exists())

    def test_baja_logica_conserva_el_usuario_y_su_historial(self):
        url = reverse('usuario_cambiar_estado', args=[self.empleado.pk])
        self.client.post(url)
        self.empleado.refresh_from_db()
        self.assertFalse(self.empleado.is_active)
        self.assertTrue(RegistroActividad.objects.filter(accion='DESACTIVACION_USUARIO').exists())
        self.client.post(url)
        self.empleado.refresh_from_db()
        self.assertTrue(self.empleado.is_active)

    def test_baja_logica_cierra_la_sesion_activa(self):
        otro = self.client_class()
        otro.force_login(self.empleado)
        self.client.post(reverse('usuario_cambiar_estado', args=[self.empleado.pk]))
        self.assertEqual(otro.get(reverse('asistencia_marcar')).status_code, 302)

    def test_no_puede_desactivarse_a_si_mismo(self):
        respuesta = self.client.post(reverse('usuario_cambiar_estado', args=[self.admin.pk]))
        self.assertEqual(respuesta.status_code, 403)

    def test_administrador_no_puede_modificar_superusuarios(self):
        root = Usuario.objects.create_superuser('root', 'root@test.bo', CLAVE)
        for vista in ('usuario_editar', 'usuario_resetear_clave'):
            self.assertEqual(self.client.get(reverse(vista, args=[root.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('usuario_cambiar_estado', args=[root.pk])).status_code, 404)

    def test_busqueda_y_filtros(self):
        url = reverse('usuario_lista')
        self.assertContains(self.client.get(url, {'q': '2222222'}), 'cajero')
        respuesta = self.client.get(url, {'rol': Group.objects.get(name=roles.EMPLEADO).pk})
        self.assertEqual([u.username for u in respuesta.context['pagina']], ['empleado'])
        parcial = self.client.get(url, {'q': 'emple'}, HTTP_HX_REQUEST='true')
        self.assertTemplateUsed(parcial, 'core/usuarios/_tabla.html')
        self.assertTemplateNotUsed(parcial, 'base.html')


class PantallasTests(TestCase):
    """Recorre todas las pantallas con los datos de prueba para detectar errores de plantilla."""

    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos_prueba', stdout=StringIO())

    def test_todas_las_pantallas_responden(self):
        from caja.models import SesionCaja
        from inventario.models import Articulo, Categoria, Ingreso, Proveedor, Traspaso
        from ventas.models import Venta
        venta, sesion = Venta.objects.get(), SesionCaja.objects.get()
        articulo, categoria, proveedor = Articulo.objects.first(), Categoria.objects.first(), Proveedor.objects.first()
        ingreso, traspaso = Ingreso.objects.first(), Traspaso.objects.first()
        otro = Usuario.objects.get(username='empleado1')
        urls = [
            reverse('inicio'), reverse('password_change'),
            reverse('usuario_lista'), reverse('usuario_crear'),
            reverse('usuario_editar', args=[otro.pk]), reverse('usuario_resetear_clave', args=[otro.pk]),
            reverse('actividad_lista'), reverse('sucursal_lista'), reverse('sucursal_crear'),
            reverse('sucursal_editar', args=[otro.sucursal_id]),
            reverse('mi_caja'), reverse('caja_todas'), reverse('caja_detalle', args=[sesion.pk]),
            reverse('venta_lista'), reverse('venta_detalle', args=[venta.pk]), reverse('venta_nota', args=[venta.pk]),
            reverse('venta_anular', args=[venta.pk]),
            reverse('venta_reporte'), reverse('venta_reporte') + '?vista=vendedores',
            reverse('venta_reporte') + '?vista=productos&formato=csv',
            reverse('cliente_lista'), reverse('cliente_crear'), reverse('cliente_detalle', args=[venta.cliente_id]),
            reverse('cliente_editar', args=[venta.cliente_id]), reverse('receta_crear', args=[venta.cliente_id]),
            reverse('receta_detalle', args=[venta.orden.receta_id]), reverse('orden_lista'),
            reverse('orden_detalle', args=[venta.orden.pk]), reverse('parametros'),
            reverse('asistencia_mia'), reverse('asistencia_reporte'), reverse('asistencia_reporte') + '?formato=csv',
            reverse('asistencia_reporte_empleado', args=[otro.pk]), reverse('personal_lista'),
            reverse('empleado_ficha', args=[otro.pk]), reverse('horario_lista'), reverse('horario_crear'),
            reverse('ausencia_lista'), reverse('feriado_lista'),
            reverse('asistencia_marcar'), reverse('asistencia_mi_historial'), reverse('asistencia_todas'),
            reverse('articulo_lista'), reverse('articulo_crear'), reverse('articulo_detalle', args=[articulo.pk]),
            reverse('articulo_editar', args=[articulo.pk]), reverse('categoria_lista'), reverse('categoria_crear'),
            reverse('categoria_editar', args=[categoria.pk]), reverse('proveedor_lista'), reverse('proveedor_crear'),
            reverse('proveedor_editar', args=[proveedor.pk]), reverse('kardex', args=[articulo.pk]),
            reverse('ingreso_lista'), reverse('ingreso_crear'), reverse('ingreso_detalle', args=[ingreso.pk]),
            reverse('ajuste_lista'), reverse('ajuste_crear'),
            reverse('traspaso_lista'), reverse('traspaso_crear'), reverse('traspaso_detalle', args=[traspaso.pk]),
            reverse('alertas_stock'), reverse('reporte_existencias'), reverse('reporte_valorado'),
            reverse('reporte_existencias') + '?formato=csv', reverse('reporte_valorado') + '?formato=csv',
        ]
        self.client.force_login(Usuario.objects.get(username='administrador'))
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.client.force_login(Usuario.objects.get(username='cajero1'))
        self.assertEqual(self.client.get(reverse('mi_caja')).status_code, 200)
        self.assertEqual(self.client.get(reverse('venta_detalle', args=[venta.pk])).status_code, 200)


class PrepararDemoTests(TestCase):
    def test_reinicia_la_demo_y_conserva_superusuarios(self):
        from django.core.management.base import CommandError
        from django.test import override_settings

        from caja.models import SesionCaja
        from inventario.models import Articulo, Categoria, Proveedor
        from ventas.models import Venta

        call_command('cargar_datos_prueba', stdout=StringIO())
        root = Usuario.objects.create_superuser('root', 'root@test.bo', CLAVE)
        # Un artículo de prueba modificado para apuntar a una categoría y un proveedor de ensayo.
        articulo = Articulo.objects.get(codigo='ARM-001')
        articulo.categoria = Categoria.objects.create(nombre='Ensayo')
        articulo.proveedor = Proveedor.objects.create(razon_social='Proveedor de ensayo')
        articulo.precio_venta = Decimal('1')
        articulo.save()
        Articulo.objects.create(codigo='ENS-1', nombre='Ensayo', categoria=articulo.categoria, precio_venta=1)
        ensayo = crear_usuario('ensayo', roles.EMPLEADO, Sucursal.objects.first(), ci='7777777')
        RegistroActividad.objects.create(accion='CREACION_USUARIO', usuario=root, usuario_afectado=ensayo)
        cajero = Usuario.objects.get(username='cajero1')
        cajero.set_password('cambiada')
        cajero.save()

        with self.assertRaises(CommandError):  # fuera de DEBUG se niega
            call_command('preparar_demo', '--si', stdout=StringIO())
        with override_settings(DEBUG=True):
            call_command('preparar_demo', '--si', stdout=StringIO())

        self.assertFalse(Usuario.objects.filter(username='ensayo').exists())
        self.assertTrue(Usuario.objects.filter(username='root').exists())
        self.assertFalse(RegistroActividad.objects.exists())
        cajero.refresh_from_db()
        self.assertTrue(cajero.check_password('Casimiro2026!'))
        # Queda el escenario de ejemplo: una caja cerrada con una venta con saldo.
        self.assertEqual(SesionCaja.objects.count(), 1)
        self.assertEqual(Venta.objects.get().saldo, Decimal('300'))
        # El catálogo vuelve al de prueba.
        self.assertFalse(Articulo.objects.filter(codigo='ENS-1').exists())
        self.assertFalse(Categoria.objects.filter(nombre='Ensayo').exists())
        self.assertFalse(Proveedor.objects.filter(razon_social='Proveedor de ensayo').exists())
        self.assertEqual(Articulo.objects.get(codigo='ARM-001').precio_venta, Decimal('350'))
        # El inventario de prueba se regenera una sola vez, con el costo promedio de las compras de prueba.
        from inventario.models import Existencia, Traspaso
        arm = Articulo.objects.get(codigo='ARM-001')
        self.assertEqual(arm.costo_promedio, Decimal('157.5'))
        self.assertEqual(sorted(Existencia.objects.filter(articulo=arm).values_list('sucursal__nombre', 'cantidad')),
                         [('Sucursal Centro', 11), ('Sucursal Norte', 4)])  # 12 en Centro, menos 1 vendido
        self.assertEqual(Traspaso.objects.filter(estado=Traspaso.Estado.ENVIADO).count(), 1)
        venta = Venta.objects.get()
        self.assertEqual((venta.subtotal, venta.descuento, venta.detalles.count()), (Decimal('710'), Decimal('60'), 2))

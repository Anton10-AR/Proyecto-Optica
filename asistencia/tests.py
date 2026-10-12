from django.core.exceptions import ValidationError
from django.urls import reverse

from asistencia import servicios
from asistencia.models import Marcacion
from core import roles
from core.tests import BaseTest, crear_usuario

# Sucursal de prueba: (-19.0475, -65.2593), radio 100 m.
DENTRO = ('-19.0476', '-65.2594')   # ~15 m
FUERA = ('-19.0500', '-65.2593')    # ~280 m


class AsistenciaTests(BaseTest):
    def test_distancia_haversine(self):
        self.assertAlmostEqual(servicios.distancia_metros(-19.0475, -65.2593, -19.0500, -65.2593), 278, delta=2)

    def test_marcacion_dentro_del_radio_alterna_entrada_y_salida(self):
        primera = servicios.registrar_marcacion(self.empleado, *DENTRO)
        segunda = servicios.registrar_marcacion(self.empleado, *DENTRO)
        tercera = servicios.registrar_marcacion(self.empleado, *DENTRO)
        self.assertEqual([primera.tipo, segunda.tipo, tercera.tipo],
                         [Marcacion.Tipo.ENTRADA, Marcacion.Tipo.SALIDA, Marcacion.Tipo.ENTRADA])
        self.assertEqual((primera.usuario, primera.sucursal), (self.empleado, self.sucursal))

    def test_marcacion_fuera_del_radio_se_rechaza(self):
        with self.assertRaises(ValidationError):
            servicios.registrar_marcacion(self.empleado, *FUERA)
        self.assertFalse(Marcacion.objects.exists())

    def test_marcacion_requiere_sucursal(self):
        sin_sucursal = crear_usuario('sinsucursal', roles.EMPLEADO, None, ci='9999999')
        with self.assertRaises(ValidationError):
            servicios.registrar_marcacion(sin_sucursal, *DENTRO)

    def test_vista_marca_al_usuario_autenticado(self):
        self.client.force_login(self.empleado)
        self.client.post(reverse('asistencia_marcar'), {'latitud': DENTRO[0], 'longitud': DENTRO[1]})
        self.assertEqual(Marcacion.objects.get().usuario, self.empleado)

    def test_historial_personal_solo_muestra_lo_propio(self):
        servicios.registrar_marcacion(self.empleado, *DENTRO)
        servicios.registrar_marcacion(self.cajero, *DENTRO)
        self.client.force_login(self.empleado)
        pagina = self.client.get(reverse('asistencia_mi_historial')).context['pagina']
        self.assertEqual({m.usuario for m in pagina}, {self.empleado})

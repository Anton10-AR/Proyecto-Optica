"""Horarios, cálculo de atrasos, faltas y horas, permisos, feriados y reportes (RF17–RF20, RF26–RF28)."""

from datetime import date, datetime, time, timedelta

from django.urls import reverse
from django.utils import timezone

from asistencia import calculo
from asistencia.calculo import EstadoDia, EstadoTramo
from asistencia.forms import HorarioForm
from asistencia.models import AsignacionHorario, Ausencia, Feriado, Horario, Marcacion, TramoHorario
from core import roles
from core.models import Configuracion
from core.tests import BaseTest, crear_usuario

LUNES = date(2026, 10, 5)  # semana del lunes 5 al domingo 11 de octubre de 2026


def momento(fecha, hora):
    return timezone.make_aware(datetime.combine(fecha, time.fromisoformat(hora)))


class AsistenciaCalculoTests(BaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.rrhh = crear_usuario('rrhh', roles.RRHH, cls.sucursal, ci='4444444')
        cls.gerente = crear_usuario('gerente', roles.GERENTE, cls.sucursal, ci='6666666')
        cls.partido = Horario.objects.create(nombre='Partido')
        tramos = [(d, '08:30', '12:30') for d in range(5)] + [(d, '14:30', '19:30') for d in range(5)] + [(5, '09:00', '13:00')]
        TramoHorario.objects.bulk_create([
            TramoHorario(horario=cls.partido, dia_semana=d, hora_entrada=time.fromisoformat(e), hora_salida=time.fromisoformat(s))
            for d, e, s in tramos])
        AsignacionHorario.objects.create(usuario=cls.empleado, horario=cls.partido, desde=LUNES - timedelta(days=7),
                                         registrado_por=cls.rrhh)

    def marcar(self, fecha, *horas, usuario=None):
        """Marcaciones alternadas entrada/salida a las horas indicadas."""
        usuario = usuario or self.empleado
        for i, hora in enumerate(horas):
            m = Marcacion.objects.create(usuario=usuario, sucursal=self.sucursal, latitud=0, longitud=0,
                                         distancia_metros=0, tipo=Marcacion.Tipo.ENTRADA if i % 2 == 0 else Marcacion.Tipo.SALIDA)
            Marcacion.objects.filter(pk=m.pk).update(fecha_hora=momento(fecha, hora))

    def semana(self, ahora=None, usuario=None):
        usuario = usuario or self.empleado
        return calculo.calcular([usuario], LUNES, LUNES + timedelta(days=6),
                                ahora=ahora or momento(LUNES + timedelta(days=6), '20:00'))[usuario.pk]

    # ---------- Cálculo (RF19) ----------

    def test_puntual_atraso_y_horas(self):
        # Mañana: 5 min tarde, dentro de la tolerancia (10). Tarde: 15 min tarde, se cuenta desde las 14:30.
        self.marcar(LUNES, '08:35', '12:31', '14:45', '19:30')
        dia = self.semana().dias[0]
        self.assertEqual(dia.estado, EstadoDia.ASISTIO)
        self.assertEqual([(t.estado, t.atraso) for t in dia.tramos],
                         [(EstadoTramo.PUNTUAL, 0), (EstadoTramo.ATRASO, 15)])
        self.assertEqual(dia.horas, timedelta(hours=8, minutes=41))
        # Con una tolerancia de 20 minutos, la tarde también es puntual.
        configuracion = Configuracion.actual()
        configuracion.tolerancia_minutos = 20
        configuracion.save()
        self.assertEqual(self.semana().dias[0].atraso, 0)

    def test_semana_completa(self):
        self.marcar(LUNES, '08:25', '12:30', '14:28', '19:31')                # lunes: puntual
        self.marcar(LUNES + timedelta(days=1), '08:29', '12:35')              # martes: no vuelve en la tarde
        # miércoles: sin marcaciones → falta
        Feriado.objects.create(fecha=LUNES + timedelta(days=3), nombre='Feriado de prueba')  # jueves
        Ausencia.objects.create(usuario=self.empleado, tipo=Ausencia.Tipo.VACACION, desde=LUNES + timedelta(days=4),
                                hasta=LUNES + timedelta(days=4), registrado_por=self.rrhh)  # viernes
        # sábado: sin marcaciones → falta; domingo: descanso
        resumen = self.semana()
        self.assertEqual([d.estado for d in resumen.dias], [
            EstadoDia.ASISTIO, EstadoDia.ASISTIO, EstadoDia.FALTA, EstadoDia.FERIADO, EstadoDia.AUSENCIA,
            EstadoDia.FALTA, EstadoDia.DESCANSO])
        self.assertEqual((resumen.laborables, resumen.asistidos, resumen.faltas), (4, 2, 2))
        self.assertEqual((resumen.tramos_sin_marcar, resumen.ausencias, resumen.feriados, resumen.atrasos), (1, 1, 1, 0))
        self.assertEqual(resumen.dias[3].etiqueta, 'Feriado de prueba')

    def test_hoy_no_es_falta_hasta_que_terminan_los_tramos(self):
        a_media_manana = momento(LUNES, '10:00')
        dia = self.semana(ahora=a_media_manana).dias[0]
        self.assertEqual((dia.estado, len(self.semana(ahora=a_media_manana).dias)), (EstadoDia.EN_CURSO, 1))
        # Marcó la mañana y aún no llega la tarde: asistió, con el tramo de la tarde pendiente.
        self.marcar(LUNES, '08:31')
        dia = self.semana(ahora=momento(LUNES, '13:00')).dias[0]
        self.assertEqual((dia.estado, dia.tramos[1].estado, dia.salida_sin_marcar),
                         (EstadoDia.ASISTIO, EstadoTramo.PENDIENTE, False))

    def test_salida_sin_marcar_y_horas_fuera_de_horario(self):
        self.marcar(LUNES, '08:30')                                  # olvidó marcar la salida
        self.marcar(LUNES + timedelta(days=6), '10:00', '12:00')     # trabajó el domingo, sin horario
        resumen = self.semana()
        self.assertTrue(resumen.dias[0].salida_sin_marcar)
        self.assertEqual(resumen.dias[0].horas, timedelta())
        self.assertEqual((resumen.dias[6].estado, resumen.dias[6].horas), (EstadoDia.DESCANSO, timedelta(hours=2)))
        self.assertEqual(resumen.salidas_sin_marcar, 1)

    def test_el_horario_vale_desde_su_fecha(self):
        manana = Horario.objects.create(nombre='Mañana')
        TramoHorario.objects.create(horario=manana, dia_semana=2, hora_entrada=time(9), hora_salida=time(13))
        AsignacionHorario.objects.create(usuario=self.empleado, horario=manana, desde=LUNES + timedelta(days=2),
                                         registrado_por=self.rrhh)
        resumen = self.semana()
        self.assertEqual(len(resumen.dias[1].tramos), 2)                    # martes: horario partido
        self.assertEqual(resumen.dias[2].tramos[0].inicio.hour, 9)          # miércoles: nuevo horario
        self.assertEqual(resumen.dias[3].estado, EstadoDia.DESCANSO)        # jueves: sin tramos en el nuevo
        sin_horario = crear_usuario('nuevo', roles.EMPLEADO, self.sucursal, ci='5555555')
        self.assertFalse(self.semana(usuario=sin_horario).con_horario)

    # ---------- Horarios (RF17) ----------

    def horario_form(self, **tramos):
        return HorarioForm({'nombre': 'Prueba', 'activo': 'on', **tramos})

    def test_validacion_del_horario(self):
        casos = [
            ({'d0_e1': '08:30'}, 'indique la entrada y la salida'),
            ({'d0_e1': '12:30', 'd0_s1': '08:30'}, 'debe ser antes de la salida'),
            ({'d0_e1': '08:30', 'd0_s1': '12:30', 'd0_e2': '12:00', 'd0_s2': '15:00'}, 'después del tramo 1'),
            ({'d0_e2': '14:30', 'd0_s2': '19:30'}, 'complete primero el tramo 1'),
            ({}, 'al menos un tramo'),
        ]
        for datos, mensaje in casos:
            with self.subTest(datos=datos):
                form = self.horario_form(**datos)
                self.assertFalse(form.is_valid())
                self.assertIn(mensaje, str(form.errors))
        form = self.horario_form(d0_e1='08:30', d0_s1='12:30', d0_e2='14:30', d0_s2='19:30', d5_e1='09:00', d5_s1='13:00')
        self.assertTrue(form.is_valid(), form.errors)
        horario = form.save()
        self.assertEqual(horario.tramos.count(), 3)
        # Al editar, los tramos se reemplazan.
        form = HorarioForm({'nombre': 'Prueba', 'activo': 'on', 'd1_e1': '09:00', 'd1_s1': '17:00'}, instance=horario)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(list(horario.tramos.values_list('dia_semana', flat=True)), [1])
        self.assertIn('Ya existe', str(HorarioForm({'nombre': 'PARTIDO', 'd0_e1': '08:00', 'd0_s1': '12:00'}).errors))

    # ---------- Permisos, feriados y pantallas (RF26–RF28, RF20) ----------

    def test_ausencias_no_se_cruzan(self):
        self.client.force_login(self.rrhh)
        datos = {'usuario': self.empleado.pk, 'tipo': 'PERMISO', 'desde': '2026-10-05', 'hasta': '2026-10-06'}
        self.assertRedirects(self.client.post(reverse('ausencia_lista'), datos), reverse('ausencia_lista'))
        cruzada = self.client.post(reverse('ausencia_lista'), {**datos, 'desde': '2026-10-06', 'hasta': '2026-10-08'})
        self.assertContains(cruzada, 'se cruza con esas fechas')
        invertida = self.client.post(reverse('ausencia_lista'), {**datos, 'desde': '2026-10-09', 'hasta': '2026-10-08'})
        self.assertContains(invertida, 'posterior a la fecha de inicio')
        ausencia = Ausencia.objects.get()
        self.client.post(reverse('ausencia_eliminar', args=[ausencia.pk]))
        self.assertFalse(Ausencia.objects.exists())

    def test_feriados_y_ficha_del_empleado(self):
        self.client.force_login(self.rrhh)
        self.client.post(reverse('feriado_lista'), {'fecha': '2026-12-25', 'nombre': 'Navidad'})
        self.assertContains(self.client.post(reverse('feriado_lista'), {'fecha': '2026-12-25', 'nombre': 'Otra'}),
                            'Ya hay un feriado en esa fecha')
        self.assertContains(self.client.get(reverse('feriado_lista'), {'anio': 2026}), 'Navidad')
        ficha = reverse('empleado_ficha', args=[self.empleado.pk])
        self.client.post(ficha, {'accion': 'cargo', 'cargo-cargo': 'Auxiliar de taller'})
        self.client.post(ficha, {'accion': 'asignar', 'asignar-horario': self.partido.pk, 'asignar-desde': '2026-11-01'})
        self.empleado.refresh_from_db()
        self.assertEqual(self.empleado.cargo, 'Auxiliar de taller')
        self.assertEqual(self.empleado.asignaciones_horario.count(), 2)
        repetida = self.client.post(ficha, {'accion': 'asignar', 'asignar-horario': self.partido.pk,
                                            'asignar-desde': '2026-11-01'})
        self.assertContains(repetida, 'ya tiene un horario asignado desde esa fecha')

    def test_reportes_y_permisos(self):
        self.marcar(LUNES, '08:45', '12:30')
        rango = {'desde': '2026-10-05', 'hasta': '2026-10-05'}
        self.client.force_login(self.gerente)
        reporte = self.client.get(reverse('asistencia_reporte'), rango)
        fila = next(r for r in reporte.context['resumenes'] if r.usuario == self.empleado)
        self.assertEqual((fila.asistidos, fila.atrasos, fila.minutos_atraso, fila.tramos_sin_marcar), (1, 1, 15, 1))
        csv = self.client.get(reverse('asistencia_reporte'), {**rango, 'formato': 'csv'}).content.decode('utf-8-sig')
        self.assertTrue(csv.startswith('Empleado;Cargo;Sucursal;Días laborables'))
        detalle = self.client.get(reverse('asistencia_reporte_empleado', args=[self.empleado.pk]), rango)
        self.assertContains(detalle, '15 min')
        # El gerente ve reportes pero no gestiona horarios; RR.HH. sí.
        self.assertEqual(self.client.get(reverse('horario_lista')).status_code, 403)
        self.client.force_login(self.rrhh)
        for nombre in ('personal_lista', 'horario_lista', 'horario_crear', 'ausencia_lista', 'feriado_lista',
                       'asistencia_reporte'):
            with self.subTest(vista=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)
        # El empleado consulta solo lo suyo.
        self.client.force_login(self.empleado)
        self.assertEqual(self.client.get(reverse('asistencia_mia'), rango).context['resumen'].atrasos, 1)
        for nombre in ('asistencia_reporte', 'personal_lista', 'ausencia_lista', 'feriado_lista'):
            with self.subTest(vista=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 403)

    def test_parametros_por_seccion(self):
        self.client.force_login(self.rrhh)
        pagina = self.client.get(reverse('parametros'))
        self.assertEqual([s[0] for s in pagina.context['secciones']], ['asistencia'])
        self.client.post(reverse('parametros'), {'seccion': 'asistencia', 'asistencia-tolerancia_minutos': '15'})
        self.assertEqual(Configuracion.actual().tolerancia_minutos, 15)
        # RR.HH. no puede cambiar el anticipo mínimo.
        respuesta = self.client.post(reverse('parametros'), {'seccion': 'ventas', 'ventas-anticipo_minimo_porcentaje': '5'})
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Configuracion.actual().anticipo_minimo_porcentaje, 50)
        self.client.force_login(self.gerente)
        self.assertEqual(len(self.client.get(reverse('parametros')).context['secciones']), 2)

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Sistema de Ventas, Almacenes/Inventario y Control de Asistencia para **Ópticas Casimiro**. Es el proyecto de la materia SIS301 Análisis y Diseño de Sistemas (USFX, Ing. Ramiro Durán), desarrollado por un equipo de tres estudiantes.

La fuente de los requisitos es el documento de visión v2, `../Documento_Vision_Opticas_Casimiro_v2.docx`, con RF01–RF32 y RNF01–RNF08. Los RF están agrupados por módulo y los nuevos se numeraron desde el RF21, así que la numeración no es correlativa dentro de cada módulo. `../Documento_Vision_Opticas_Casimiro.pdf` es la versión anterior y `../VISIÓN DEL PROYECTO.pdf` es la plantilla de la materia.

Para leer los archivos en este equipo, donde no hay pandoc ni pdftoppm:
- PDF: `pdftotext -layout -enc UTF-8 <archivo> -`
- DOCX: `python -c "import zipfile,re,sys; x=zipfile.ZipFile(sys.argv[1]).read('word/document.xml').decode(); print(re.sub(r'<[^>]+>','',re.sub(r'</w:p>','\n',x)))" <archivo>`

- **AppSheet quedó descartado.** No hay que migrar datos ni lógica. El módulo de asistencia se desarrolla desde cero.
- **Fuera del alcance de la versión 1:** app móvil nativa, facturación electrónica ante el SIN (el comprobante es una nota de venta no fiscal), planilla de sueldos, contabilidad, apertura y cierre de caja, y laboratorios externos.

## Stack

Django 6.1 con Python 3.14, PostgreSQL 18 local, HTMX para la interactividad (pendiente de agregar) y plantillas de Django. El entorno virtual está en `.venv/` (Windows).

## Comandos

```bash
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python manage.py runserver
.venv/Scripts/python manage.py makemigrations
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py createsuperuser
.venv/Scripts/python manage.py test                                          # todos los tests
.venv/Scripts/python manage.py test ventas                                   # una app
.venv/Scripts/python manage.py test ventas.tests.NombreTest.test_metodo      # un test
.venv/Scripts/python manage.py check
```

La configuración se lee de `.env` con python-dotenv (ver `.env.example`). Sin `DJANGO_SECRET_KEY`, `settings.py` falla al cargar. La base de datos se llama `optica_casimiro` y hay que crearla en PostgreSQL antes del primer `migrate`.

Después de instalar un paquete, regenera `requirements.txt` con `.venv/Scripts/python -m pip freeze > requirements.txt`.

## Arquitectura

Es un monolito modular: un proyecto Django (`config/`) con una app por módulo del documento de visión, todas sobre una sola base de datos.

| App | Módulo | Requisitos |
|---|---|---|
| `core` | Usuarios, roles y elementos compartidos | RNF03 |
| `ventas` | Ventas, clientes, comprobantes y reportes | RF01–RF07 |
| `inventario` | Artículos, proveedores, ingresos/salidas, kardex y alertas de stock | RF08–RF14 |
| `asistencia` | Sucursales, horarios, tolerancia, marcaciones y reportes | RF15–RF20 |

- **Usuario personalizado:** `AUTH_USER_MODEL = 'core.Usuario'`. Usa siempre `settings.AUTH_USER_MODEL` o `get_user_model()`, nunca `django.contrib.auth.models.User`.
- **Roles:** se modelan con los `Group` de Django (Vendedor, Óptico/Técnico de taller, Almacén, RR.HH., Gerencia, Administrador) y sus permisos, no con un campo `rol` en el usuario.
- **Consistencia del stock (RNF05):** toda operación que mueva stock debe actualizar el stock y registrar el kardex dentro de una sola `transaction.atomic()`, bloqueando el artículo con `select_for_update()`. Esto incluye registrar una venta, anularla, registrar ingresos, salidas y traspasos. Pon esta lógica en funciones de servicio de `inventario`, no en vistas ni en el admin, para que `ventas` la reutilice.
- **Dependencia entre apps:** `ventas` y `asistencia` pueden depender de `inventario` y `core`, pero no al revés.
- **Panel de administración:** los CRUD simples (artículos, proveedores, sucursales, horarios, clientes) pueden resolverse con el admin de Django. Las pantallas operativas (punto de venta, marcación de asistencia, reportes) son vistas propias.
- **Plantillas y estáticos:** las plantillas globales están en `templates/` (`base.html`, `registration/login.html`). La autenticación usa las vistas de `django.contrib.auth.urls` bajo `/cuentas/`.
- **Idioma:** `LANGUAGE_CODE = 'es'` y `TIME_ZONE = 'America/La_Paz'`. Los nombres de modelos, campos y la interfaz van en español.

## Decisiones de dominio

Ya están incorporadas en el documento de visión v2. Este resumen sirve para aplicarlas al modelar y programar.

- **Receta y órdenes de trabajo:** se registra la receta del cliente con su historial: OD/OI con esfera, cilindro, eje y adición, más la distancia pupilar. La receta puede venir de un examen hecho en la óptica (se registra el óptico que lo hizo) o ser externa (se registra el médico o la institución). Cada venta de lentes graduados genera una orden de trabajo para el **taller propio**, con los estados pendiente → en taller → listo → entregado. No hay laboratorios externos.
- **Pagos:** una venta puede cobrarse en varios pagos (anticipo y saldo a la entrega). Cada pago lleva su propia forma de pago (efectivo, QR, tarjeta). No hay apertura ni cierre de caja.
- **Stock por sucursal:** cada sucursal tiene sus propias existencias. Los traspasos del RF10 mueven mercadería entre sucursales y generan una salida en el origen y un ingreso en el destino.
- **Kardex valorado por promedio ponderado:** cada ingreso recalcula el costo promedio del artículo. Las salidas se valoran al costo promedio vigente.
- **Entrega con saldo:** una orden de trabajo no puede marcarse como entregada si la venta tiene saldo pendiente, salvo que el gerente lo autorice. La autorización registra quién la dio y cuándo. Las ventas de lentes graduados exigen un anticipo mínimo, configurable como porcentaje.
- **Horario partido:** un horario laboral admite varios tramos por día (por ejemplo, 8:30–12:30 y 14:30–19:30). El atraso se calcula en la entrada de cada tramo y las horas trabajadas suman todos los tramos.
- **Faltas:** RR.HH. registra permisos y vacaciones por empleado y mantiene un calendario de feriados. Esos días no cuentan como falta.
- **Marcación por geolocalización:** el navegador envía la ubicación al marcar. La marcación se acepta solo si está dentro del radio configurado de la sucursal, que guarda su latitud, longitud y radio. La geolocalización del navegador exige HTTPS, salvo en `localhost`.

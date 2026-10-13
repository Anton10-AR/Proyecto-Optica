# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Sistema de Ventas, Almacenes/Inventario y Control de Asistencia para **Ópticas Casimiro**. Es el proyecto de la materia SIS301 Análisis y Diseño de Sistemas (USFX, Ing. Ramiro Durán), desarrollado por un equipo de tres estudiantes.

La fuente de los requisitos es el documento de visión v2, `../Documento_Vision_Opticas_Casimiro_v2.docx`, con RF01–RF36 y RNF01–RNF08. Los RF están agrupados por módulo y los nuevos se numeraron desde el RF21, así que la numeración no es correlativa dentro de cada módulo. `../Documento_Vision_Opticas_Casimiro.pdf` es la versión anterior y `../VISIÓN DEL PROYECTO.pdf` es la plantilla de la materia. El documento de visión se genera con `docs/vision/generar_vision.js` (docx-js). Para cambiarlo, edita el script y regenéralo: `cd docs/vision && npm install && node generar_vision.js "../../../Documento_Vision_Opticas_Casimiro_v2.docx"`. No edites el .docx a mano: el próximo regenerado borraría esos cambios.

El proyecto se entrega por etapas. La segunda entrega (Gestión de Usuarios) se documenta en `docs/gestion_usuarios.md`, que incluye el diagrama ER, la matriz de permisos, la guía de demostración y los scripts SQL de `docs/sql/`.

Para leer los archivos en este equipo, donde no hay pandoc ni pdftoppm:
- PDF: `pdftotext -layout -enc UTF-8 <archivo> -`
- DOCX: `python -c "import zipfile,re,sys; x=zipfile.ZipFile(sys.argv[1]).read('word/document.xml').decode(); print(re.sub(r'<[^>]+>','',re.sub(r'</w:p>','\n',x)))" <archivo>`

- **AppSheet quedó descartado.** No hay que migrar datos ni lógica. El módulo de asistencia se desarrolla desde cero.
- **Fuera del alcance de la versión 1:** app móvil nativa, facturación electrónica ante el SIN (el comprobante es una nota de venta no fiscal), planilla de sueldos, contabilidad y laboratorios externos.

## Stack

Django 6.1 con Python 3.14, PostgreSQL 18 local, plantillas de Django con Bootstrap 5.3, Bootstrap Icons, HTMX y la fuente Inter, todos copiados en `static/vendor/` (sin CDN ni paso de compilación, para que la demostración funcione sin internet). Contraseñas con Argon2 (`argon2-cffi`). El entorno virtual está en `.venv/` (Windows).

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
.venv/Scripts/python manage.py configurar_roles       # crea/sincroniza los grupos según core/roles.py
.venv/Scripts/python manage.py cargar_datos_prueba    # roles, sucursales y un usuario por rol (clave Casimiro2026!)
.venv/Scripts/python manage.py matriz_permisos        # imprime la matriz rol-permiso en Markdown
.venv/Scripts/python manage.py preparar_demo          # borra operaciones, auditoría y usuarios de ensayo y recarga los datos de prueba (solo con DEBUG)
```

Los tests crean una base de datos temporal en PostgreSQL, así que el usuario de `.env` necesita permiso `CREATEDB`. `core/tests.py` define `BaseTest` y `crear_usuario`, que reutilizan los tests de las demás apps.

La configuración se lee de `.env` con python-dotenv (ver `.env.example`). Sin `DJANGO_SECRET_KEY`, `settings.py` falla al cargar. La base de datos se llama `optica_casimiro` y hay que crearla en PostgreSQL antes del primer `migrate`.

Después de instalar un paquete, regenera `requirements.txt` con `.venv/Scripts/python -m pip freeze > requirements.txt`.

## Arquitectura

Es un monolito modular: un proyecto Django (`config/`) con una app por módulo del documento de visión, todas sobre una sola base de datos.

| App | Módulo | Requisitos |
|---|---|---|
| `core` | Usuarios, roles, sucursales, auditoría y elementos compartidos | RF16, RF29, RF30, RF36, RNF03 |
| `inventario` | Artículos, proveedores, ingresos/salidas, kardex y alertas de stock (aún vacía) | RF08–RF14 |
| `caja` | Apertura, movimientos y cierre de caja con arqueo | RF33–RF35 |
| `ventas` | Ventas, pagos, nota de venta, recetas, órdenes de trabajo y reportes | RF01–RF07, RF21–RF25, RF31–RF32 |
| `asistencia` | Marcaciones, horarios, tolerancia, permisos, feriados y reportes | RF15, RF17–RF20, RF26–RF28 |

`ventas` tiene por ahora solo el encabezado de la venta (descripción y total). El detalle de productos se agregará cuando exista `inventario`.

- **Usuario personalizado:** `AUTH_USER_MODEL = 'core.Usuario'`. Usa siempre `settings.AUTH_USER_MODEL` o `get_user_model()`, nunca `django.contrib.auth.models.User`.
- **Roles (RBAC):** un rol es un `Group` de Django. `Usuario.rol` (FK a `Group`) es la fuente de verdad, y `Usuario.save()` sincroniza `groups` con ella, porque Django consulta los permisos a través de los grupos. Los permisos de cada rol se definen solo en `core/roles.py` (`ROLES` y `PERMISOS`). Para cambiarlos, edita ese archivo y ejecuta `configurar_roles`; no los asignes desde el admin. Cuando agregues un modelo o permiso nuevo, inclúyelo en `PERMISOS` para que aparezca en la matriz.
- **Control de acceso en vistas:** usa permisos, no nombres de rol: `@permission_required(..., raise_exception=True)` o `PermisoMixin` de `core/views.py`. Para "ver lo propio o todo", sigue el patrón de los permisos `ver_todas_*` (por ejemplo `ventas.ver_todas_ventas`). El menú de `templates/base.html` se arma con `perms`.
- **Cuentas:** el login acepta usuario o correo (`core/backends.py`). La baja es lógica (`is_active=False`), y todas las FK hacia el usuario son `PROTECT`, así que nunca se borra un usuario. Una contraseña creada o reseteada por el administrador marca `debe_cambiar_clave`, y `core.middleware.CambioClaveObligatorioMiddleware` obliga a cambiarla. Un administrador que no es superusuario no puede modificar superusuarios (`usuarios_gestionables`).
- **Auditoría:** las acciones de seguridad se registran con `core.auditoria.registrar(Accion.X, request, afectado=...)`. Los inicios y cierres de sesión, y los intentos fallidos, se registran solos mediante las señales de `core/signals.py`.
- **Servicios:** la lógica de negocio va en `servicios.py` de cada app (`caja.servicios`, `ventas.servicios`, `asistencia.servicios`) y lanza `ValidationError` con mensajes para el usuario. Las vistas solo validan formularios y muestran los mensajes. Cobrar un pago siempre pasa por `ventas.servicios.registrar_pago`, que crea el `MovimientoCaja` en la caja abierta del usuario dentro de la misma transacción.
- **Formularios y plantillas:** los formularios heredan de `core.forms.BootstrapMixin`, y las plantillas los dibujan con `{% include '_campos.html' %}`, o con `with columnas=2` para dos columnas.
- **Diseño visual:** la paleta y los componentes propios (`.oc-encabezado`, `.oc-indicador`, `.oc-estado-*`, `.btn-acento`) están en `static/css/casimiro.css` y documentados en `docs/identidad_visual.md`. Cada pantalla empieza con `.oc-encabezado` (ícono de Bootstrap Icons, título y acción principal) y pone las tablas dentro de `.card`. No uses colores hex sueltos: usa las variables `--oc-*` o las clases de Bootstrap ya ajustadas.
- **Inicio:** `config/views.py:inicio` combina datos de todas las apps y vive a nivel de proyecto para que `core` no dependa de las demás. Cada bloque del panel se muestra según un permiso.
- **Consistencia del stock (RNF05):** toda operación que mueva stock debe actualizar el stock y registrar el kardex dentro de una sola `transaction.atomic()`, bloqueando el artículo con `select_for_update()`. Esto incluye registrar una venta, anularla, registrar ingresos, salidas y traspasos. Pon esta lógica en funciones de servicio de `inventario`, no en vistas ni en el admin, para que `ventas` la reutilice.
- **Dependencia entre apps:** `core` no depende de ninguna. `caja` y `asistencia` dependen de `core`. `ventas` depende de `core`, `caja` y, más adelante, de `inventario`. Nunca al revés.
- **Panel de administración:** el admin de Django (`/admin/`) es solo para superusuarios (`is_staff`). Los roles del sistema trabajan con vistas propias, incluidos los CRUD.
- **Plantillas y URLs:** todas las plantillas están en `templates/<app>/`. La autenticación está en `/cuentas/` (login, logout y cambio de contraseña, con vistas propias de `core/views.py`). La administración de usuarios y sucursales está en `/administracion/`.
- **Idioma:** `LANGUAGE_CODE = 'es'` y `TIME_ZONE = 'America/La_Paz'`. Los nombres de modelos, campos y la interfaz van en español.

## Decisiones de dominio

Ya están incorporadas en el documento de visión v2. Este resumen sirve para aplicarlas al modelar y programar.

- **Receta y órdenes de trabajo:** se registra la receta del cliente con su historial: OD/OI con esfera, cilindro, eje y adición, más la distancia pupilar. La receta puede venir de un examen hecho en la óptica (se registra el óptico que lo hizo) o ser externa (se registra el médico o la institución). Cada venta de lentes graduados genera una orden de trabajo para el **taller propio**, con los estados pendiente → en taller → listo → entregado. No hay laboratorios externos.
- **Pagos y caja:** una venta puede cobrarse en varios pagos (anticipo y saldo a la entrega). Cada pago lleva su propia forma de pago (efectivo, QR, tarjeta) y se registra como ingreso en la caja abierta de quien cobra. Cada usuario tiene como máximo una caja abierta (restricción en la base de datos). El arqueo compara solo el efectivo: monto inicial + ingresos − egresos en efectivo. Caja se incorporó en la segunda entrega porque el enunciado del docente la exige.
- **Stock por sucursal:** cada sucursal tiene sus propias existencias. Los traspasos del RF10 mueven mercadería entre sucursales y generan una salida en el origen y un ingreso en el destino.
- **Kardex valorado por promedio ponderado:** cada ingreso recalcula el costo promedio del artículo. Las salidas se valoran al costo promedio vigente.
- **Entrega con saldo:** una orden de trabajo no puede marcarse como entregada si la venta tiene saldo pendiente, salvo que el gerente lo autorice. La autorización registra quién la dio y cuándo. Las ventas de lentes graduados exigen un anticipo mínimo, configurable como porcentaje.
- **Horario partido:** un horario laboral admite varios tramos por día (por ejemplo, 8:30–12:30 y 14:30–19:30). El atraso se calcula en la entrada de cada tramo y las horas trabajadas suman todos los tramos.
- **Faltas:** RR.HH. registra permisos y vacaciones por empleado y mantiene un calendario de feriados. Esos días no cuentan como falta.
- **Marcación por geolocalización:** el navegador envía la ubicación al marcar. La marcación se acepta solo si está dentro del radio configurado de la sucursal, que guarda su latitud, longitud y radio. La geolocalización del navegador exige HTTPS, salvo en `localhost`.

# Ópticas Casimiro

**Sistema Informático de Ventas, Almacenes/Inventario y Control de Asistencia**

Proyecto de la materia SIS301 Análisis y Diseño de Sistemas · Universidad Mayor Real y Pontificia de San Francisco Xavier de Chuquisaca · Docente: Ing. Ramiro Durán · Sucre, 2026.

Equipo: Aguilar Rosales Carla Fátima · Avendaño Retamozo Juan Antonio · Cueto Chavez Abigail Fernanda.

## Estado del proyecto

| Entrega | Contenido | Estado |
|---|---|---|
| 1 | Documento de visión (actualizado a la v2) | Listo |
| 2 | Gestión de usuarios: autenticación, roles (RBAC), CRUD de usuarios, auditoría e integración con caja, ventas y asistencia | Terminada |
| Sistema completo | Inventario, ventas completas (clientes, recetas, órdenes de trabajo, reportes) y asistencia completa (horarios, permisos, feriados, reportes). Los 36 requisitos funcionales están implementados (ver la [revisión de requisitos](docs/revision_requisitos.md)) | Terminado |

## Tecnologías

- **Backend:** Python 3.14 y Django 6.1, con el patrón MVT y una app por módulo.
- **Base de datos:** PostgreSQL (desarrollado con la versión 18).
- **Interfaz:** plantillas de Django con Bootstrap 5.3, Bootstrap Icons y HTMX. Todo está incluido en `static/vendor/`, así que funciona sin internet.
- **Seguridad:** contraseñas con Argon2 y sesiones en base de datos con expiración por inactividad.

## Instalación (Windows)

Necesita **Python 3.12 o superior**, **PostgreSQL** y **Git**. Los comandos son para PowerShell, desde la carpeta del proyecto.

**1. Clonar el repositorio**

```powershell
git clone https://github.com/Anton10-AR/Proyecto-Optica.git
cd Proyecto-Optica
```

**2. Crear el entorno virtual e instalar las dependencias**

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

**3. Crear la base de datos en PostgreSQL** (pide la contraseña del usuario `postgres`)

```powershell
psql -U postgres -c "CREATE DATABASE optica_casimiro;"
```

Si `psql` no se reconoce, use la ruta completa, por ejemplo `& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "..."`.

**4. Configurar el archivo `.env`**

```powershell
copy .env.example .env
```

Abra `.env` y complete estos valores:

- `DB_PASSWORD`: la contraseña de su usuario de PostgreSQL. Si tiene espacios o `#`, enciérrela entre comillas simples.
- `DJANGO_SECRET_KEY`: una clave propia. Para generarla, ejecute:
  ```powershell
  .venv\Scripts\python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
  ```

`.env` es personal y **no se sube al repositorio**.

**5. Crear las tablas y cargar los datos de prueba**

```powershell
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py preparar_demo --si
```

**6. Levantar el servidor**

```powershell
.venv\Scripts\python manage.py runserver
```

Abra http://127.0.0.1:8000/. Para entrar al panel de Django (`/admin/`), cree su propio superusuario con `.venv\Scripts\python manage.py createsuperuser`.

## Usuarios de prueba

Todos tienen la contraseña **`Casimiro2026!`**. También se puede ingresar con el correo, por ejemplo `cajero1@opticascasimiro.test`.

| Usuario | Rol |
|---|---|
| `administrador` | Administrador |
| `gerente` | Gerente |
| `cajero1`, `cajero2` | Cajero/Vendedor |
| `rrhh` | Recursos Humanos |
| `almacen` | Encargado de almacén |
| `optico` | Óptico/Técnico de taller |
| `empleado1`, `empleado2` | Empleado |
| `exempleado` | Empleado, con la cuenta desactivada |

`preparar_demo` devuelve la base a este estado inicial: borra las operaciones de los ensayos (ventas, cajas, marcaciones, movimientos de inventario, clientes, permisos), la auditoría y los usuarios de ensayo, y recarga los datos de prueba. Úselo el mismo día de cada demostración, porque los datos se arman alrededor de la fecha en que se cargan. El recorrido completo está en la [guía de demostración](docs/guia_demostracion.md).

## Comandos útiles

```powershell
.venv\Scripts\python manage.py test                    # pruebas automatizadas
.venv\Scripts\python manage.py test core               # pruebas de una app
.venv\Scripts\python manage.py preparar_demo           # reinicia los datos de la demostración
.venv\Scripts\python manage.py configurar_roles        # aplica los permisos definidos en core/roles.py
.venv\Scripts\python manage.py matriz_permisos         # imprime la matriz de permisos por rol
```

Las pruebas crean una base de datos temporal, así que el usuario de PostgreSQL de `.env` necesita permiso para crear bases de datos (`postgres` lo tiene).

## Estructura

| Carpeta | Contenido |
|---|---|
| `config/` | Configuración de Django, URLs y página de inicio |
| `core/` | Usuarios, roles y permisos, sucursales, auditoría y parámetros del negocio |
| `caja/` | Apertura, movimientos y arqueo de caja |
| `ventas/` | Ventas, pagos, nota de venta, clientes, recetas, órdenes de trabajo y reportes de ventas |
| `inventario/` | Catálogo, existencias por sucursal, compras, bajas y ajustes, traspasos, kardex, alertas y reportes |
| `asistencia/` | Marcación con geolocalización, horarios, permisos, feriados y reportes de asistencia |
| `templates/`, `static/` | Pantallas, estilos, logo y librerías |
| `docs/` | Documentación de las entregas |

## Documentación

- [`docs/guia_demostracion.md`](docs/guia_demostracion.md): guía única para presentar todo el sistema, con los usuarios, los datos de prueba y qué hacer si algo falla.
- [`docs/revision_requisitos.md`](docs/revision_requisitos.md): estado de cada requisito del documento de visión (RF01–RF36 y RNF01–RNF08).
- [`docs/gestion_usuarios.md`](docs/gestion_usuarios.md): segunda entrega. Incluye el diagrama entidad-relación, la matriz de permisos completa y el cumplimiento del enunciado.
- [`docs/inventario.md`](docs/inventario.md), [`docs/recetas_ordenes.md`](docs/recetas_ordenes.md), [`docs/asistencia.md`](docs/asistencia.md) y [`docs/reportes_ventas.md`](docs/reportes_ventas.md): diagrama, permisos, reglas de negocio y pruebas de cada módulo.
- [`docs/capturas/`](docs/capturas/): capturas de las pantallas principales, con lo que muestra cada una.
- [`docs/identidad_visual.md`](docs/identidad_visual.md): paleta de colores, tipografía y componentes de la interfaz.
- [`docs/sql/`](docs/sql/): scripts SQL del esquema y de los datos de prueba.
- [`docs/vision/`](docs/vision/): generador del documento de visión en Word.

## Trabajo en equipo

- **Al empezar a trabajar:** ejecute `git pull` para traer los cambios de los demás.
- **Si alguien agregó migraciones:** después del `pull`, ejecute `.venv\Scripts\python manage.py migrate`.
- **Si cambió `requirements.txt`:** vuelva a ejecutar `.venv\Scripts\python -m pip install -r requirements.txt`.
- **Antes de subir sus cambios:** ejecute las pruebas.

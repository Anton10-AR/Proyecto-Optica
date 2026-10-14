# Capturas de pantalla · Gestión de Usuarios

Capturas del sistema con los datos de prueba (`preparar_demo`), tomadas a 1366 × 860 px. Siguen el orden del recorrido de la demostración. Todos los datos son ficticios.

Los pies de figura numerados para el informe están en [`subtitulos.md`](subtitulos.md).

## Inicio de sesión y control de acceso

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 01 | [01_login.png](01_login.png) | — | Inicio de sesión con usuario o correo y aviso de cierre por inactividad |
| 02 | [02_login_rechazado.png](02_login_rechazado.png) | `exempleado` | Cuenta desactivada: el ingreso se rechaza (baja lógica) |
| 05 | [05_acceso_denegado.png](05_acceso_denegado.png) | `empleado1` | Un empleado intenta abrir *Usuarios*: acceso denegado por su rol (RBAC) |
| 22 | [22_cambio_clave_obligatorio.png](22_cambio_clave_obligatorio.png) | `rvargas` | Primer ingreso con contraseña inicial: el sistema obliga a cambiarla |

## Inicio según el rol

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 03 | [03_inicio_empleado.png](03_inicio_empleado.png) | `empleado1` | Menú reducido: solo *Inicio* y *Asistencia* |
| 12 | [12_inicio_cajero.png](12_inicio_cajero.png) | `cajero1` | Caja abierta y ventas del día; menús de *Ventas* y *Caja* |
| 19 | [19_inicio_administrador.png](19_inicio_administrador.png) | `administrador` | Indicadores de usuarios, asistencia, intentos fallidos y actividad reciente |

## Administración de usuarios (CRUD)

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 14 | [14_usuario_validaciones.png](14_usuario_validaciones.png) | `administrador` | Validaciones: CI y correo duplicados, teléfono inválido, rol obligatorio y contraseñas distintas |
| 15 | [15_usuarios_lista.png](15_usuarios_lista.png) | `administrador` | Usuario creado; tabla con rol, sucursal, estado y acciones |
| 16 | [16_usuarios_busqueda.png](16_usuarios_busqueda.png) | `administrador` | Búsqueda en vivo por nombre ("vargas") |
| 17 | [17_usuario_editar.png](17_usuario_editar.png) | `administrador` | Edición de datos personales, rol y sucursal |
| 18 | [18_resetear_clave.png](18_resetear_clave.png) | `administrador` | Reseteo de contraseña por el administrador |
| 21 | [21_sucursales.png](21_sucursales.png) | `administrador` | Sucursales con su ubicación y radio de marcación |
| 23 | [23_registro_actividad.png](23_registro_actividad.png) | `administrador` | Auditoría: inicios de sesión, intentos fallidos, creación y desactivación de cuentas |

## Integración con Caja y Ventas

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 07 | [07_caja_cerrada.png](07_caja_cerrada.png) | `cajero1` | Apertura de caja e historial de cajas cerradas |
| 08 | [08_nueva_venta.png](08_nueva_venta.png) | `cajero1` | Registro de venta con el vendedor autenticado |
| 09 | [09_venta_registrada.png](09_venta_registrada.png) | `cajero1` | Venta con anticipo: vendedor (ID), pagos y saldo pendiente |
| 10 | [10_mi_caja_abierta.png](10_mi_caja_abierta.png) | `cajero1` | Caja abierta: los pagos de las ventas entran como ingresos y el efectivo esperado se calcula solo |
| 11 | [11_nota_de_venta.png](11_nota_de_venta.png) | `cajero1` | Nota de venta imprimible con el vendedor en el encabezado |
| 13 | [13_arqueo_caja.png](13_arqueo_caja.png) | `cajero1` | Caja cerrada con arqueo: efectivo esperado frente a contado |
| 24 | [24_ventas_gerente.png](24_ventas_gerente.png) | `gerente` | El gerente ve las ventas de todos los vendedores |

## Integración con Asistencia

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 04 | [04_marcar_asistencia.png](04_marcar_asistencia.png) | `empleado1` | Entrada registrada dentro del radio de la sucursal (9 m); el botón pasa a *Marcar salida* |
| 06 | [06_mi_historial.png](06_mi_historial.png) | `empleado1` | Historial personal de entradas y salidas |
| 20 | [20_asistencia_personal.png](20_asistencia_personal.png) | `administrador` | Marcaciones de todo el personal, con filtros por empleado y fecha |

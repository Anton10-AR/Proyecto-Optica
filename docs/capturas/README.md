# Capturas de pantalla

Capturas del sistema con los datos de prueba (`preparar_demo`), tomadas a 1366 × 860 px. Todos los datos son ficticios.

- **01 a 25:** recorrido de la segunda entrega (inicio de sesión, usuarios, caja, ventas y asistencia), tomadas de nuevo con el sistema actual.
- **26 a 49:** sistema completo: inventario, clientes, recetas y órdenes de trabajo, reportes y asistencia. Siguen el recorrido de la [guía de demostración](../guia_demostracion.md).

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
| 12 | [12_inicio_cajero.png](12_inicio_cajero.png) | `cajero1` | Caja, ventas del día, órdenes de trabajo y alertas de stock |
| 19 | [19_inicio_administrador.png](19_inicio_administrador.png) | `administrador` | Indicadores de todos los módulos, intentos fallidos y actividad reciente |

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
| 24 | [24_historial_contrasenas.png](24_historial_contrasenas.png) | `administrador` | Historial de contraseñas: cambio hecho por el usuario y reseteo hecho por el administrador, con fecha, hora, cuenta afectada e IP |

## Integración con Caja y Ventas

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 07 | [07_caja_cerrada.png](07_caja_cerrada.png) | `cajero1` | Apertura de caja e historial de cajas cerradas |
| 08 | [08_nueva_venta.png](08_nueva_venta.png) | `cajero1` | Registro de venta: cliente, artículos con precio y stock, descuento y total en vivo |
| 09 | [09_venta_registrada.png](09_venta_registrada.png) | `cajero1` | Venta con anticipo: vendedor (ID), artículos, descuento, pagos y saldo pendiente |
| 10 | [10_mi_caja_abierta.png](10_mi_caja_abierta.png) | `cajero1` | Caja abierta: los pagos de las ventas entran como ingresos y el efectivo esperado se calcula solo |
| 11 | [11_nota_de_venta.png](11_nota_de_venta.png) | `cajero1` | Nota de venta imprimible con el vendedor en el encabezado |
| 13 | [13_arqueo_caja.png](13_arqueo_caja.png) | `cajero1` | Caja cerrada con arqueo: efectivo esperado frente a contado |
| 25 | [25_ventas_gerente.png](25_ventas_gerente.png) | `gerente` | El gerente ve las ventas de todos los vendedores |

## Integración con Asistencia

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 04 | [04_marcar_asistencia.png](04_marcar_asistencia.png) | `empleado1` | Entrada registrada dentro del radio de la sucursal (9 m), con el horario del día; el botón pasa a *Marcar salida* |
| 06 | [06_mi_historial.png](06_mi_historial.png) | `empleado1` | Historial personal de entradas y salidas |
| 20 | [20_asistencia_personal.png](20_asistencia_personal.png) | `administrador` | Marcaciones de todo el personal, con filtros por empleado y fecha |

## Inventario

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 26 | [26_articulos.png](26_articulos.png) | `almacen` | Catálogo con búsqueda, categoría y stock total |
| 27 | [27_kardex.png](27_kardex.png) | `almacen` | Kardex valorado: compra, traspaso, baja, venta y reposición por anulación |
| 28 | [28_ingreso.png](28_ingreso.png) | `almacen` | Ingreso por compra con sus líneas y total |
| 29 | [29_traspaso_por_recibir.png](29_traspaso_por_recibir.png) | `cajero2` | Traspaso en camino: solo la sucursal de destino puede confirmarlo |
| 30 | [30_alertas_stock.png](30_alertas_stock.png) | `almacen` | Alertas de stock mínimo con stock disponible en otras sucursales |
| 31 | [31_inventario_valorado.png](31_inventario_valorado.png) | `gerente` | Inventario valorado consolidado, por categoría |

## Clientes, recetas y órdenes de trabajo

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 32 | [32_cliente_ficha.png](32_cliente_ficha.png) | `cajero1` | Ficha del cliente: historial de recetas, compras y órdenes |
| 33 | [33_receta_nueva.png](33_receta_nueva.png) | `optico` | Registro de una receta de examen (OD/OI, DP y óptico responsable) |
| 34 | [34_venta_anticipo_insuficiente.png](34_venta_anticipo_insuficiente.png) | `cajero1` | Venta de lentes graduados rechazada por anticipo menor al mínimo |
| 35 | [35_venta_con_orden.png](35_venta_con_orden.png) | `cajero1` | Venta registrada con su orden de trabajo generada |
| 36 | [36_ordenes_trabajo.png](36_ordenes_trabajo.png) | `optico` | Órdenes de trabajo filtradas por estado |
| 37 | [37_orden_entrega_bloqueada.png](37_orden_entrega_bloqueada.png) | `cajero1` | Orden lista con saldo: la entrega queda bloqueada |
| 38 | [38_orden_autorizar_gerente.png](38_orden_autorizar_gerente.png) | `gerente` | El gerente autoriza la entrega con saldo, con un motivo |

## Gerencia: anulación y reportes de ventas

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 39 | [39_venta_anulada.png](39_venta_anulada.png) | `gerente` | Venta anulada: stock repuesto, pago devuelto y orden anulada |
| 40 | [40_reporte_ventas.png](40_reporte_ventas.png) | `gerente` | Resumen de ventas: totales, cobros por forma de pago, anuladas y ventas por día |
| 41 | [41_reporte_ventas_producto.png](41_reporte_ventas_producto.png) | `gerente` | Ventas por producto con costo y margen |
| 49 | [49_inicio_gerente.png](49_inicio_gerente.png) | `gerente` | Inicio del gerente: caja, órdenes, alertas de stock y asistencia |

## Asistencia y parámetros

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 42 | [42_marcar_con_horario.png](42_marcar_con_horario.png) | `empleado1` | Marcación con el horario del día |
| 43 | [43_reporte_asistencia.png](43_reporte_asistencia.png) | `rrhh` | Reporte de asistencia por empleado: faltas, atrasos, permisos y horas |
| 44 | [44_asistencia_empleado.png](44_asistencia_empleado.png) | `rrhh` | Detalle día por día: atraso, tramo sin marcar, falta y feriado |
| 45 | [45_horario.png](45_horario.png) | `rrhh` | Horario partido con dos tramos por día |
| 46 | [46_permisos_vacaciones.png](46_permisos_vacaciones.png) | `rrhh` | Permisos y vacaciones por días completos |
| 47 | [47_feriados.png](47_feriados.png) | `rrhh` | Calendario de feriados del año |
| 48 | [48_parametros.png](48_parametros.png) | `gerente` | Parámetros: anticipo mínimo y tolerancia de atraso |

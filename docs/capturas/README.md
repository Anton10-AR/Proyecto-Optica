# Capturas de pantalla

Capturas del sistema con los datos de prueba (`preparar_demo`), tomadas a 1366 × 860 px. Todos los datos son ficticios.

- **01 a 24:** recorrido de la segunda entrega (inicio de sesión, usuarios, caja, ventas y asistencia), tomadas de nuevo con el sistema actual.
- **25 a 48:** sistema completo: inventario, clientes, recetas y órdenes de trabajo, reportes y asistencia. Siguen el recorrido de la [guía de demostración](../guia_demostracion.md).

Los pies de figura numerados para el informe están en [`subtitulos.md`](subtitulos.md). El documento de la entrega final con todas las figuras es [`SIS301_Entrega_Final.docx`](../SIS301_Entrega_Final.docx).

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
| 23 | [23_registro_actividad.png](23_registro_actividad.png) | `administrador` | Auditoría: inicios de sesión, intento fallido, creación y desactivación de cuentas, y cambio y reseteo de contraseña, con fecha, hora, cuenta afectada e IP |

## Integración con Caja y Ventas

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 07 | [07_caja_cerrada.png](07_caja_cerrada.png) | `cajero1` | Apertura de caja e historial de cajas cerradas |
| 08 | [08_nueva_venta.png](08_nueva_venta.png) | `cajero1` | Registro de venta: cliente, artículos con precio y stock, descuento y total en vivo |
| 09 | [09_venta_registrada.png](09_venta_registrada.png) | `cajero1` | Venta con anticipo: vendedor (ID), artículos, descuento, pagos y saldo pendiente |
| 10 | [10_mi_caja_abierta.png](10_mi_caja_abierta.png) | `cajero1` | Caja abierta: los pagos de las ventas entran como ingresos y el efectivo esperado se calcula solo |
| 11 | [11_nota_de_venta.png](11_nota_de_venta.png) | `cajero1` | Nota de venta imprimible con el vendedor en el encabezado |
| 13 | [13_arqueo_caja.png](13_arqueo_caja.png) | `cajero1` | Caja cerrada con arqueo: efectivo esperado frente a contado |
| 24 | [24_ventas_gerente.png](24_ventas_gerente.png) | `gerente` | El gerente ve las ventas de todos los vendedores |

## Integración con Asistencia

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 04 | [04_marcar_asistencia.png](04_marcar_asistencia.png) | `empleado1` | Entrada registrada dentro del radio de la sucursal (9 m), con el horario del día; el botón pasa a *Marcar salida* |
| 06 | [06_mi_historial.png](06_mi_historial.png) | `empleado1` | Historial personal de entradas y salidas |
| 20 | [20_asistencia_personal.png](20_asistencia_personal.png) | `administrador` | Marcaciones de todo el personal, con filtros por empleado y fecha |

## Inventario

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 25 | [25_articulos.png](25_articulos.png) | `almacen` | Catálogo con búsqueda, categoría y stock total |
| 26 | [26_kardex.png](26_kardex.png) | `almacen` | Kardex valorado: compra, traspaso, baja, venta y reposición por anulación |
| 27 | [27_ingreso.png](27_ingreso.png) | `almacen` | Ingreso por compra con sus líneas y total |
| 28 | [28_traspaso_por_recibir.png](28_traspaso_por_recibir.png) | `cajero2` | Traspaso en camino: solo la sucursal de destino puede confirmarlo |
| 29 | [29_alertas_stock.png](29_alertas_stock.png) | `almacen` | Alertas de stock mínimo con stock disponible en otras sucursales |
| 30 | [30_inventario_valorado.png](30_inventario_valorado.png) | `gerente` | Inventario valorado consolidado, por categoría |

## Clientes, recetas y órdenes de trabajo

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 31 | [31_cliente_ficha.png](31_cliente_ficha.png) | `cajero1` | Ficha del cliente: historial de recetas, compras y órdenes |
| 32 | [32_receta_nueva.png](32_receta_nueva.png) | `optico` | Registro de una receta de examen (OD/OI, DP y óptico responsable) |
| 33 | [33_venta_anticipo_insuficiente.png](33_venta_anticipo_insuficiente.png) | `cajero1` | Venta de lentes graduados rechazada por anticipo menor al mínimo |
| 34 | [34_venta_con_orden.png](34_venta_con_orden.png) | `cajero1` | Venta registrada con su orden de trabajo generada |
| 35 | [35_ordenes_trabajo.png](35_ordenes_trabajo.png) | `optico` | Órdenes de trabajo filtradas por estado |
| 36 | [36_orden_entrega_bloqueada.png](36_orden_entrega_bloqueada.png) | `cajero1` | Orden lista con saldo: la entrega queda bloqueada |
| 37 | [37_orden_autorizar_gerente.png](37_orden_autorizar_gerente.png) | `gerente` | El gerente autoriza la entrega con saldo, con un motivo |

## Gerencia: anulación y reportes de ventas

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 38 | [38_venta_anulada.png](38_venta_anulada.png) | `gerente` | Venta anulada: stock repuesto, pago devuelto y orden anulada |
| 39 | [39_reporte_ventas.png](39_reporte_ventas.png) | `gerente` | Resumen de ventas: totales, cobros por forma de pago, anuladas y ventas por día |
| 40 | [40_reporte_ventas_producto.png](40_reporte_ventas_producto.png) | `gerente` | Ventas por producto con costo y margen |
| 48 | [48_inicio_gerente.png](48_inicio_gerente.png) | `gerente` | Inicio del gerente: caja, órdenes, alertas de stock y asistencia |

## Asistencia y parámetros

| # | Captura | Usuario | Qué muestra |
|---|---|---|---|
| 41 | [41_marcar_con_horario.png](41_marcar_con_horario.png) | `empleado1` | Marcación con el horario del día |
| 42 | [42_reporte_asistencia.png](42_reporte_asistencia.png) | `rrhh` | Reporte de asistencia por empleado: faltas, atrasos, permisos y horas |
| 43 | [43_asistencia_empleado.png](43_asistencia_empleado.png) | `rrhh` | Detalle día por día: atraso, tramo sin marcar, falta y feriado |
| 44 | [44_horario.png](44_horario.png) | `rrhh` | Horario partido con dos tramos por día |
| 45 | [45_permisos_vacaciones.png](45_permisos_vacaciones.png) | `rrhh` | Permisos y vacaciones por días completos |
| 46 | [46_feriados.png](46_feriados.png) | `rrhh` | Calendario de feriados del año |
| 47 | [47_parametros.png](47_parametros.png) | `gerente` | Parámetros: anticipo mínimo y tolerancia de atraso |

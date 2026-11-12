# Subtítulos de las capturas

Pies de figura para el informe, en el orden de los archivos de esta carpeta: todas muestran el sistema actual. Las figuras 1 a 25 siguen el recorrido de la segunda entrega (usuarios, seguridad, caja, ventas y asistencia) y las 26 a 49 cubren los módulos agregados después. Debajo de cada figura se puede agregar *Fuente: elaboración propia.*

| Archivo | Subtítulo |
|---|---|
| `01_login.png` | **Figura 1.** Pantalla de inicio de sesión: el usuario se autentica con su nombre de usuario o su correo y su contraseña. |
| `02_login_rechazado.png` | **Figura 2.** Intento de ingreso con una cuenta desactivada: el sistema rechaza el acceso sin revelar si el usuario existe. |
| `03_inicio_empleado.png` | **Figura 3.** Panel de inicio del rol Empleado: el menú se limita a *Inicio* y *Asistencia*. |
| `04_marcar_asistencia.png` | **Figura 4.** Marcación de entrada validada por geolocalización, a 9 m de la sucursal; la pantalla muestra el horario del día y el botón cambia a *Marcar salida*. |
| `05_acceso_denegado.png` | **Figura 5.** Control de acceso basado en roles: un empleado que intenta abrir la gestión de usuarios recibe el mensaje de acceso denegado. |
| `06_mi_historial.png` | **Figura 6.** Historial personal de asistencia del empleado, con sus entradas y salidas por fecha y sucursal. |
| `07_caja_cerrada.png` | **Figura 7.** Apertura de caja del cajero/vendedor, vinculada a su usuario y sucursal, con el historial de sus cajas cerradas. |
| `08_nueva_venta.png` | **Figura 8.** Formulario de registro de venta: cliente registrado u ocasional, artículos del catálogo con su precio y stock, descuento y total calculado al instante; el vendedor es el usuario autenticado. |
| `09_venta_registrada.png` | **Figura 9.** Venta registrada con anticipo: muestra el vendedor con su ID, los artículos, el descuento, los pagos y el saldo pendiente. |
| `10_mi_caja_abierta.png` | **Figura 10.** Caja abierta: los pagos de las ventas se registran como ingresos y el sistema calcula el efectivo esperado. |
| `11_nota_de_venta.png` | **Figura 11.** Nota de venta imprimible con el vendedor en el encabezado. |
| `12_inicio_cajero.png` | **Figura 12.** Panel de inicio del rol Cajero/Vendedor: estado de su caja, ventas del día, órdenes de trabajo y alertas de stock de su sucursal. |
| `13_arqueo_caja.png` | **Figura 13.** Cierre de caja con arqueo: comparación entre el efectivo esperado y el efectivo contado. |
| `14_usuario_validaciones.png` | **Figura 14.** Validación del formulario de usuario: CI y correo duplicados, teléfono con formato inválido, rol obligatorio y contraseñas que no coinciden. |
| `15_usuarios_lista.png` | **Figura 15.** Listado de usuarios después de crear una cuenta, con su rol, sucursal, estado y acciones disponibles. |
| `16_usuarios_busqueda.png` | **Figura 16.** Búsqueda en vivo de usuarios por nombre o CI. |
| `17_usuario_editar.png` | **Figura 17.** Edición de los datos personales, el rol y la sucursal de un usuario. |
| `18_resetear_clave.png` | **Figura 18.** Reseteo de contraseña por el administrador; el usuario deberá cambiarla en su próximo ingreso. |
| `19_inicio_administrador.png` | **Figura 19.** Panel de inicio del rol Administrador: indicadores de caja, ventas, órdenes de trabajo, stock, asistencia, usuarios, intentos fallidos y actividad reciente. |
| `20_asistencia_personal.png` | **Figura 20.** Consulta de la asistencia de todo el personal, con filtros por empleado y fecha. |
| `21_sucursales.png` | **Figura 21.** Gestión de sucursales con su ubicación geográfica y el radio permitido para marcar asistencia. |
| `22_cambio_clave_obligatorio.png` | **Figura 22.** Cambio obligatorio de la contraseña inicial en el primer ingreso de un usuario nuevo. |
| `23_registro_actividad.png` | **Figura 23.** Registro de actividad (auditoría): inicios de sesión, intentos fallidos y creación y desactivación de cuentas, con fecha, hora, usuario e IP. |
| `24_historial_contrasenas.png` | **Figura 24.** Historial de contraseñas en el registro de actividad: el cambio que hizo el propio usuario y el reseteo hecho por el administrador, con fecha, hora, quién lo hizo, la cuenta afectada y la IP. Las contraseñas nunca se guardan ni se muestran. |
| `25_ventas_gerente.png` | **Figura 25.** Listado de ventas visto por el Gerente, que consulta las ventas de todos los vendedores. |
| `26_articulos.png` | **Figura 26.** Catálogo de artículos con su categoría, precio y stock total, con búsqueda por código, código de barras o nombre. |
| `27_kardex.png` | **Figura 27.** Kardex valorado por costo promedio ponderado: cada entrada y salida muestra el saldo de la sucursal, el costo promedio y el valor. |
| `28_ingreso.png` | **Figura 28.** Ingreso de mercadería por compra a un proveedor, con la factura, las cantidades y el costo de cada artículo. |
| `29_traspaso_por_recibir.png` | **Figura 29.** Traspaso entre sucursales en dos pasos: la sucursal de destino confirma la recepción para que la mercadería entre a su stock. |
| `30_alertas_stock.png` | **Figura 30.** Alertas de stock mínimo por sucursal, con las unidades disponibles en otras sucursales para decidir entre traspasar o comprar. |
| `31_inventario_valorado.png` | **Figura 31.** Reporte de inventario valorado de toda la empresa, con subtotales por categoría y exportación a CSV. |
| `32_cliente_ficha.png` | **Figura 32.** Ficha del cliente con el historial de sus recetas, sus compras y el estado de sus órdenes de trabajo. |
| `33_receta_nueva.png` | **Figura 33.** Registro de la receta oftalmológica: graduación de cada ojo, distancia pupilar y óptico responsable del examen. |
| `34_venta_anticipo_insuficiente.png` | **Figura 34.** Venta de lentes graduados con cliente y receta: el sistema exige el anticipo mínimo configurado (50 %). |
| `35_venta_con_orden.png` | **Figura 35.** Venta de lentes graduados registrada: genera la orden de trabajo para el taller con la fecha de entrega prometida. |
| `36_ordenes_trabajo.png` | **Figura 36.** Órdenes de trabajo del taller, consultadas por estado, con su fecha de entrega prometida y el saldo de la venta. |
| `37_orden_entrega_bloqueada.png` | **Figura 37.** Orden de trabajo lista con saldo pendiente: la entrega queda bloqueada hasta cobrar el saldo o contar con la autorización del gerente. |
| `38_orden_autorizar_gerente.png` | **Figura 38.** Autorización del gerente para entregar un trabajo con saldo pendiente; queda registrada con su nombre, la fecha y el motivo. |
| `39_venta_anulada.png` | **Figura 39.** Venta anulada con motivo: el stock se repone, lo pagado se devuelve desde la caja de quien anula y la orden de trabajo queda anulada. |
| `40_reporte_ventas.png` | **Figura 40.** Reporte de ventas del período: total vendido, ticket promedio, saldo por cobrar, cobros por forma de pago y ventas por día. |
| `41_reporte_ventas_producto.png` | **Figura 41.** Reporte de ventas por producto, con las unidades vendidas, el importe, el costo y el margen. |
| `42_marcar_con_horario.png` | **Figura 42.** Pantalla de marcación de asistencia, que muestra el horario partido del empleado para el día. |
| `43_reporte_asistencia.png` | **Figura 43.** Reporte de asistencia del período por empleado: días laborables, asistidos, faltas, atrasos, tramos sin marcar, permisos y horas trabajadas. |
| `44_asistencia_empleado.png` | **Figura 44.** Detalle diario de la asistencia de un empleado: atraso en un tramo, tramo sin marcar, falta, feriado y horas trabajadas. |
| `45_horario.png` | **Figura 45.** Definición de un horario partido, con dos tramos por día de lunes a viernes y uno el sábado. |
| `46_permisos_vacaciones.png` | **Figura 46.** Registro de permisos, vacaciones y bajas médicas por días completos, que no se cuentan como faltas. |
| `47_feriados.png` | **Figura 47.** Calendario de feriados, comunes a todas las sucursales, que no se cuentan como faltas. |
| `48_parametros.png` | **Figura 48.** Parámetros del negocio: anticipo mínimo para lentes graduados y tolerancia de atraso. |
| `49_inicio_gerente.png` | **Figura 49.** Panel de inicio del Gerente con indicadores de caja, ventas, órdenes de trabajo, alertas de stock, asistencia y seguridad. |

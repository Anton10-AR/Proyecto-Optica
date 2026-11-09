# Revisión de requisitos

Ópticas Casimiro · SIS301 Análisis y Diseño de Sistemas · revisión del 9 de noviembre de 2026

Este documento compara cada requisito del documento de visión v2 (RF01–RF36 y RNF01–RNF08) con lo que hace el sistema. Para cada uno indica dónde se ve, cómo se verificó y qué observaciones quedan.

**Cómo se verificó:**

- **Pruebas automatizadas:** pasan las 106 (`manage.py test`).
- **Pruebas manuales:** el equipo las hizo en el navegador al cerrar cada módulo.
- **Revisión del código y de la configuración.**
- **Mediciones de esta revisión:**
  - una prueba de carga con 10 usuarios simultáneos;
  - un recorrido de todas las rutas sin sesión iniciada;
  - capturas en el ancho de un celular (390 px).

**Estados:**

| Estado | Significado |
|---|---|
| **Cumple** | Implementado y verificado. |
| **Cumple, con observación** | Implementado, con un límite o una decisión que conviene declarar. |
| **Pendiente** | Depende del despliegue o de una prueba que no se puede hacer en el equipo de desarrollo. |

## 1. Resumen

| | Cumple | Cumple, con observación | Pendiente |
|---|:---:|:---:|:---:|
| Requisitos funcionales (36) | 32 | 4 | 0 |
| Requisitos no funcionales (8) | 4 | 1 | 3 |

Los 36 requisitos funcionales están implementados. Lo pendiente es de despliegue y de pruebas en campo: el RNF01 se mide con un vendedor real, el RNF04 y el RNF08 se resuelven al publicar el sistema con HTTPS, y el RNF07 necesita probarse en Firefox y en un iPhone.

**Defecto encontrado y corregido en esta revisión:**

- Las vistas basadas en clases (crear o editar usuarios, sucursales, artículos, categorías y proveedores, y el registro de actividad) respondían 403 a un usuario sin sesión en lugar de llevarlo al login.
- No exponían datos, pero si la sesión vencía en esas pantallas, se veía "Acceso denegado".
- Se corrigió en `core.views.PermisoMixin` y se agregó un test (`test_sin_sesion_todas_las_pantallas_llevan_al_login`).

## 2. Requisitos funcionales

### Ventas y caja

| Req. | Estado | Dónde se ve | Observación |
|---|---|---|---|
| RF01 Registrar ventas con cliente, productos y cantidades | Cumple, con observación | *Ventas → Nueva venta* | Una venta admite hasta 5 líneas de artículos. Alcanza para una óptica (armazón, dos lunas, montaje y un accesorio), pero conviene declararlo o ampliar las filas |
| RF02 Subtotales, descuentos y total | Cumple | Se calculan en vivo en el formulario y de nuevo en el servidor | El descuento es global, en Bs, y menor que el subtotal |
| RF03 Nota de venta no fiscal | Cumple | *Imprimir nota de venta* | Incluye las líneas, el descuento, los pagos, el saldo y el número de orden de trabajo |
| RF04 Consultar el stock al vender | Cumple | Cada artículo del formulario muestra el stock de la sucursal del vendedor | La venta se rechaza si falta stock |
| RF05 Datos básicos del cliente | Cumple | *Ventas → Clientes y recetas* | Una venta simple acepta un cliente ocasional, con solo el nombre |
| RF06 Anular una venta y revertir el stock | Cumple | *Anular* en el detalle de la venta | También devuelve lo pagado desde la caja de quien anula y anula la orden de trabajo |
| RF07 Reportes por período, vendedor y producto | Cumple | *Ventas → Reportes de ventas* | El importe por producto es a precio de lista |
| RF21 Receta oftalmológica | Cumple | Ficha del cliente → *Nueva receta* | Validaciones de graduación (pasos de 0,25 y eje con cilindro) |
| RF22 Historial de recetas | Cumple | Ficha del cliente | Las recetas no se editan: cada graduación nueva es una receta nueva |
| RF23 Orden de trabajo al vender lentes graduados | Cumple | Se genera con la venta | Los "lentes graduados" son los artículos marcados con *requiere receta* |
| RF24 Estados de la orden y consulta por estado | Cumple | *Ventas → Órdenes de trabajo* | Agrega el estado *anulada* cuando se anula la venta |
| RF25 Varios pagos por venta, con su forma de pago | Cumple | Detalle de la venta y de la orden | Cada pago entra a la caja abierta de quien cobra |
| RF31 Entrega con saldo solo con autorización | Cumple | Detalle de la orden | Queda registrado quién autorizó, cuándo y por qué |
| RF32 Anticipo mínimo configurable | Cumple | *Administración → Parámetros* | 50 % al iniciar |
| RF33 Abrir caja, una por usuario | Cumple | *Caja → Mi caja* | Restricción en la base de datos |
| RF34 Ingresos y egresos de caja | Cumple | *Mi caja* → movimiento | Vender y cobrar exigen la caja abierta |
| RF35 Cierre con arqueo | Cumple | *Mi caja* → cerrar | Compara solo el efectivo |

### Inventario

| Req. | Estado | Dónde se ve | Observación |
|---|---|---|---|
| RF08 Artículos y existencias por sucursal | Cumple | *Inventario → Artículos y stock* | |
| RF09 Ingresos por compra | Cumple | *Inventario → Ingresos por compra* | Recalcula el costo promedio |
| RF10 Salidas por venta, baja o traspaso | Cumple | Ventas, *Bajas y ajustes*, *Traspasos* | El traspaso tiene dos pasos: envío y recepción |
| RF11 Kardex valorado por promedio ponderado | Cumple | Detalle del artículo → *Kardex* | |
| RF12 Alertas de stock mínimo | Cumple | Indicador en el inicio y *Alertas de stock* | Indica en qué otra sucursal hay unidades |
| RF13 Proveedores | Cumple | *Inventario → Proveedores* | |
| RF14 Existencias e inventario valorado | Cumple | *Reporte de existencias* e *Inventario valorado* | Por sucursal y de toda la empresa |

### Asistencia

| Req. | Estado | Dónde se ve | Observación |
|---|---|---|---|
| RF15 Marcación con geolocalización | Cumple | *Asistencia → Marcar* | Fuera de `localhost` necesita HTTPS (ver RNF08) |
| RF16 Sucursales con ubicación y radio | Cumple | *Administración → Sucursales* | |
| RF17 Horarios con varios tramos por día | Cumple, con observación | *Personal y horarios → Horarios* | La pantalla admite **dos** tramos por día, que cubre el horario partido. El modelo admite más |
| RF18 Tolerancia y otros parámetros | Cumple, con observación | *Administración → Parámetros* | El único parámetro de asistencia es la tolerancia. "Otros parámetros" puede retirarse del requisito o detallarse |
| RF19 Atrasos, faltas y horas | Cumple | `asistencia/calculo.py` | Por tramo, sin contar feriados ni permisos |
| RF20 Reportes por empleado, sucursal y período | Cumple | *Asistencia → Reporte de asistencia* | Con detalle día por día y CSV |
| RF26 Datos de los empleados | Cumple, con observación | *Usuarios* y *Personal y horarios* | RR.HH. edita el cargo y el horario. Los datos personales y la sucursal los edita el Administrador, porque son también los datos de la cuenta |
| RF27 Permisos y vacaciones | Cumple | *Asistencia → Permisos y vacaciones* | Por días completos, sin cruces. Incluye bajas médicas |
| RF28 Calendario de feriados | Cumple | *Asistencia → Feriados* | Se cargaron los de 2026 |

### Usuarios y seguridad

| Req. | Estado | Dónde se ve | Observación |
|---|---|---|---|
| RF29 Usuarios, roles y baja lógica | Cumple | *Administración → Usuarios* | 7 roles |
| RF30 Inicio de sesión obligatorio | Cumple | Todas las rutas | Se recorrieron las 77 rutas sin sesión. Todas las pantallas llevan al login (tras la corrección de esta revisión). Las acciones que solo aceptan POST (cobrar, avanzar una orden, cerrar sesión…) responden 405 a un GET y tampoco muestran datos |
| RF36 Registro de actividad | Cumple | *Administración → Registro de actividad* | |

## 3. Requisitos no funcionales

| Req. | Estado | Verificación | Observación |
|---|---|---|---|
| RNF01 Venta completa en menos de 3 minutos | Pendiente | Se mide cronometrando a un vendedor después de una capacitación de 1 hora | La pantalla está pensada para eso: el cliente y su receta se eligen solos desde la ficha, y el total y el anticipo se calculan en vivo |
| RNF02 Menos de 2 s con 10 usuarios | Cumple | Prueba de carga: 10 usuarios simultáneos y 220 pedidos a las 11 pantallas más pesadas, sin errores. Peor caso: **0,94 s** (reporte de asistencia); mediana de 0,3 a 0,8 s | Se midió en el servidor de desarrollo con los datos de prueba. Conviene repetirla en el servidor final con más datos |
| RNF03 Acceso por rol, Argon2 y sesión de 30 minutos | Cumple | Matriz de permisos, `PASSWORD_HASHERS` con Argon2 y `SESSION_COOKIE_AGE = 1800` renovado en cada pedido (probado con la sesión en 60 s) | |
| RNF04 Disponibilidad del 99 % en el horario de atención | Pendiente | Depende del servidor donde se publique | Falta definir dónde se aloja, el respaldo diario de PostgreSQL y el reinicio automático del servicio |
| RNF05 Venta, stock y kardex en una transacción | Cumple | Tests de reversión: sin stock no se registra ni la venta ni el pago | Igual en ingresos, ajustes, traspasos y anulaciones |
| RNF06 Módulos independientes | Cumple | Una app de Django por módulo, con dependencias en un solo sentido (`core` ← `caja`, `asistencia`, `inventario` ← `ventas`) | |
| RNF07 Chrome, Edge y Firefox, en computadora y celular | Cumple, con observación | Revisado en Edge (Chromium) a 1300 px y a 390 px de ancho: el menú se pliega y no hay desplazamiento horizontal | Falta probar en Firefox y en Safari de iOS. En el celular, el selector de artículo de *Nueva venta* queda angosto y corta el texto |
| RNF08 Computadora con red en cada punto y HTTPS | Pendiente | El sistema corre en `localhost`, donde la geolocalización funciona sin HTTPS | Para publicarlo hace falta un dominio con certificado, `DEBUG=False`, servir los estáticos (`collectstatic`) y activar `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` y `SECURE_SSL_REDIRECT` |

## 4. Acciones antes de la entrega

| Acción | Estado |
|---|---|
| **Documento de visión:** incorporar las decisiones tomadas al desarrollar | **Hecho.** Nueva sección 4.7 *Reglas de negocio*: cliente ocasional, recetas que no se editan, lentes graduados, anulación con devolución, tolerancia, tramo sin marcar, permisos por días, orden anulada y quién edita los datos del empleado |
| **Observaciones RF01, RF17 y RF18** | **Hecho.** Las 5 líneas por venta y los 2 tramos por día se declararon como límites de la versión 1 (sección 4.6). El RF18 dice ahora «los parámetros… como la tolerancia de atraso». El RF24 y el RF26 se precisaron |
| **Guía de demostración** única y `preparar_demo` probado en una base nueva | **Hecho.** [`guia_demostracion.md`](guia_demostracion.md) |
| **README** con el estado actual | **Hecho** |
| **Pruebas en campo:** cronometrar una venta (RNF01) y probar en Firefox y en un iPhone (RNF07) | Pendiente, a cargo del equipo |
| **Despliegue con HTTPS** (RNF04 y RNF08) | Pendiente, solo si se publica el sistema. Para la defensa en clase basta `localhost`, donde funcionan todos los módulos, incluida la geolocalización |
| **Capturas** de `docs/capturas/` con los módulos nuevos | Pendiente |

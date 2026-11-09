# Guía de demostración

Ópticas Casimiro · SIS301 Análisis y Diseño de Sistemas

Esta guía reúne en un solo recorrido la demostración de todo el sistema. Se calcula para 25 minutos y se puede recortar por bloques. El detalle de cada módulo está en sus documentos:

- [`gestion_usuarios.md`](gestion_usuarios.md)
- [`inventario.md`](inventario.md)
- [`recetas_ordenes.md`](recetas_ordenes.md)
- [`asistencia.md`](asistencia.md)
- [`reportes_ventas.md`](reportes_ventas.md)

## 1. Antes de presentar

**El mismo día de la presentación**, porque los datos de prueba se arman alrededor de la fecha en que se cargan (ayer, las últimas dos semanas…):

```bash
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py preparar_demo --si
.venv/Scripts/python manage.py runserver
```

- `preparar_demo` borra todo lo hecho en los ensayos (ventas, cajas, marcaciones, movimientos, clientes, permisos, auditoría y sesiones) y recarga los datos de prueba. Los superusuarios se conservan. Solo funciona con `DJANGO_DEBUG=True`.
- Abra **http://127.0.0.1:8000** o **http://localhost:8000**, no la IP de la red: la geolocalización solo funciona en `localhost` o con HTTPS.
- No hace falta internet: Bootstrap, los íconos, HTMX y la tipografía están dentro del proyecto.
- Prepare una ventana normal y otra **de incógnito**, para cambiar de usuario sin cerrar sesión.
- La sesión vence a los **30 minutos sin actividad**.
- Cierre los programas que no use; el equipo trabaja mejor con memoria libre.

**Lista de control:**

- [ ] `preparar_demo` ejecutado hoy y servidor en marcha.
- [ ] Inicio de sesión probado con `administrador`.
- [ ] Simulación de ubicación lista (paso 4.1).
- [ ] Ventana de incógnito abierta.

## 2. Usuarios de prueba

Todos tienen la contraseña **`Casimiro2026!`**. También se puede entrar con el correo, por ejemplo `cajero1@opticascasimiro.test`.

| Usuario | Rol | Sucursal | Para mostrar |
|---|---|---|---|
| `administrador` | Administrador | Centro | Usuarios, sucursales, registro de actividad y acceso a todo |
| `gerente` | Gerente | Centro | Reportes, anulación de ventas, autorización de entregas con saldo y parámetros |
| `cajero1` | Cajero/Vendedor | Centro | Caja, ventas, clientes, recetas externas y entrega de trabajos |
| `cajero2` | Cajero/Vendedor | Norte | Recepción del traspaso pendiente; no ve las ventas de `cajero1` |
| `optico` | Óptico/Técnico de taller | Centro | Recetas de examen y avance de las órdenes en el taller |
| `almacen` | Encargado de almacén | Centro | Compras, traspasos, kardex, alertas e inventario valorado |
| `rrhh` | Recursos Humanos | Centro | Horarios, permisos, feriados, tolerancia y reportes de asistencia |
| `empleado1` | Empleado | Centro | Marcación por geolocalización y *Mi asistencia* |
| `empleado2` | Empleado | Norte | Horario de medio tiempo y una vacación |
| `exempleado` | Empleado | Centro | **Cuenta desactivada**: el inicio de sesión se rechaza |

**Lo que deja cargado `preparar_demo`:**

| Módulo | Datos |
|---|---|
| Catálogo | 9 artículos: armazones, lunas, lentes de contacto, accesorios y 2 servicios. Las lunas LUN-001 y LUN-002 son lentes graduados |
| Inventario | 3 compras (el costo de ARM-001 queda en Bs 157,50), 1 traspaso Centro → Norte ya recibido, **1 traspaso pendiente de recepción**, 1 baja y **6 alertas de stock mínimo** |
| Clientes | **María Fernanda López Rojas**, con 2 recetas de examen; **Carlos Vargas Soliz**, con una receta externa con adición; **Rosa Quiroga Mendoza**, sin recetas |
| Ventas | Ayer, `cajero1` vendió a María un armazón y dos lunas: total Bs 650 y anticipo Bs 350. Su caja quedó cerrada con arqueo. **La orden de trabajo 000001 está lista para entregar con un saldo de Bs 300** |
| Asistencia | Horario partido para todos (medio tiempo para `empleado2`), feriados de 2026 y dos semanas de marcaciones. `empleado1` tiene un atraso de 22 minutos, un tramo sin marcar y una falta. `cajero1` tiene un atraso de 11 minutos y un permiso. `empleado2` tiene una vacación de tres días |
| Parámetros | Anticipo mínimo del 50 % y tolerancia de 10 minutos |

## 3. Recorrido sugerido

### 3.1 Acceso y seguridad (3 min)

1. Intente entrar como `exempleado`: el sistema rechaza la cuenta desactivada.
2. Entre como `empleado1`. El menú muestra solo *Asistencia*. Escriba `/administracion/usuarios/` en la barra de direcciones: aparece *Acceso denegado*.
3. Entre como `administrador`, abra *Administración → Usuarios*, cree un usuario y búsquelo por nombre o CI.
4. Abra *Registro de actividad*: aparecen el intento rechazado, los inicios de sesión y la creación del usuario.
5. Opcional: entre con el usuario recién creado. El sistema obliga a cambiar la contraseña inicial.

### 3.2 Venta de lentes graduados, del examen a la entrega (8 min)

Es el recorrido central: une clientes, recetas, ventas, inventario, caja y taller.

1. **Receta:** como `optico`, abra *Ventas → Clientes y recetas* → Rosa Quiroga → **Nueva receta**. Registre un examen; si escribe una esfera que no sea múltiplo de 0,25 o un eje sin cilindro, el sistema lo indica.
2. **Venta:** como `cajero1`, abra su caja (*Caja → Mi caja*, monto inicial Bs 200). Desde la ficha de Rosa pulse **Nueva venta**: el cliente y su receta ya están elegidos.
   - Agregue un armazón ARM-001, dos lunas LUN-001 (marcadas «con receta») y el montaje SRV-002. El total y el anticipo mínimo se calculan mientras escribe.
   - Intente pagar menos del 50 %: la venta se rechaza. Pague el anticipo y registre la venta. Se genera la orden de trabajo.
   - Muestre la **nota de venta** imprimible, con el vendedor y el número de orden.
3. **Stock:** en *Inventario → Artículos y stock* → ARM-001 → **Kardex**, como `almacen` o `gerente`, aparece la *Salida por venta*. El servicio de montaje no mueve stock.
4. **Taller:** como `optico`, en *Ventas → Órdenes de trabajo*, abra la orden nueva y pulse **Pasar al taller** y luego **Marcar como listo**. El historial registra quién hizo cada paso.
5. **Entrega con saldo (RF31):** abra la orden **000001** de María, lista y con saldo de Bs 300.
   - Como `cajero1`, el botón **Entregar al cliente** está desactivado.
   - Como `gerente`, escriba un motivo y pulse **Autorizar**.
   - Vuelva como `cajero1` y entregue. El historial muestra quién autorizó y quién entregó.
   - La otra vía: cobrar el saldo desde la misma orden, y la entrega queda habilitada sin autorización.
6. **Caja:** como `cajero1`, cierre la caja con el efectivo contado. El arqueo calcula la diferencia.

### 3.3 Inventario (5 min)

1. Como `almacen`, el inicio muestra el indicador de **stock mínimo**. *Inventario → Alertas de stock* indica, para cada alerta, si hay unidades en otra sucursal (para traspasar) o si hay que comprar.
2. *Ingresos por compra → Nuevo ingreso*: compre ARM-001 a otro costo. En el kardex, el costo promedio se recalcula.
3. *Traspasos → Nuevo traspaso*: pida más unidades de las que hay. El sistema rechaza todo el traspaso, no solo la línea que falla.
4. Como `cajero2` (Sucursal Norte), *Inventario → Traspasos* avisa que hay uno por recibir. Ábralo y pulse **Confirmar recepción**: la mercadería entra al stock de Norte.
5. Como `gerente`, *Inventario → Inventario valorado*: valor por sucursal y de toda la empresa, con subtotales por categoría. Exporte el CSV.

### 3.4 Asistencia (5 min)

1. **Marcación:** como `empleado1`, abra *Asistencia → Marcar entrada/salida*. La pantalla muestra su horario de hoy. Pulse **Marcar entrada** y permita la ubicación. Fuera de la facultad, simule la ubicación (paso 4.1). Para mostrar el rechazo, simule una ubicación lejana.
2. **Reporte:** como `rrhh`, abra *Asistencia → Reporte de asistencia* y elija las dos últimas semanas. Entre al detalle de Luis Fernández (`empleado1`): un atraso de 22 minutos, una tarde «sin marcar», una falta y el feriado de Todos Santos.
3. **Tolerancia:** en *Administración → Parámetros* súbala a 25 minutos. El atraso de 22 minutos desaparece del reporte, porque el cálculo es en vivo. Vuélvala a 10.
4. **Permiso:** en *Permisos y vacaciones*, registre un permiso para `empleado1` el día de su falta. En el reporte, ese día pasa a «Permiso».
5. Opcional: en *Personal y horarios → Horarios*, cree un horario y asígnelo a un empleado desde mañana. Los días anteriores no cambian.

### 3.5 Gerencia (4 min)

1. Como `gerente`, abra *Ventas → Reportes de ventas*: el resumen del mes (total, ticket promedio, cobros por forma de pago y ventas por día), la vista por vendedor y la vista por producto, con costo y margen.
2. **Anulación:** abra su caja con un monto inicial de Bs 1 000 o más, entre a la venta que hizo `cajero1` y pulse **Anular** con un motivo.
   - El stock vuelve al kardex como *Reposición por venta anulada*.
   - Lo pagado sale de la caja del gerente.
   - La orden de trabajo queda anulada.
3. En el reporte de ventas, la venta anulada ya no suma y aparece aparte.

## 4. Si algo falla

### 4.1 La marcación dice que está fuera del radio

Las dos sucursales de prueba están en la Facultad de Ciencias y Tecnología (latitud `-19.039699`, longitud `-65.256900`, radio de 300 m). Para simular la ubicación en Chrome o Edge:

1. Abra las herramientas de desarrollo (F12) → ⋮ → *More tools* → *Sensors*.
2. En *Location*, elija *Other…*.
3. Escriba latitud `-19.039780` y longitud `-65.256980` (a unos 12 m) y marque de nuevo.

Para mostrar el rechazo, use latitud `-19.050000` (a unos 1,1 km).

### 4.2 Otros problemas

| Problema | Solución |
|---|---|
| El navegador no pide la ubicación | Abra el sistema en `localhost` o `127.0.0.1`, no con la IP de la red |
| «Debe abrir su caja antes de registrar ventas» | *Caja → Mi caja* → abrir, con un monto inicial |
| Al anular: «Abra su caja para devolver lo pagado» | Quien anula necesita su caja abierta; con pagos en efectivo, con un monto inicial que alcance para la devolución |
| «Stock insuficiente» en una venta o traspaso | Es una validación. Elija menos unidades o compre más en *Ingresos por compra* |
| El reporte de asistencia muestra una falta hoy | El día en curso cuenta en tiempo real: un tramo que ya terminó sin marcar es falta |
| Se cerró la sesión sola | Pasaron 30 minutos sin actividad (RNF03); vuelva a entrar |
| Los datos no coinciden con esta guía | Ejecute de nuevo `preparar_demo --si` |

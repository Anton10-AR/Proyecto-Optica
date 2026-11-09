# Reportes de ventas

Ópticas Casimiro · SIS301 Análisis y Diseño de Sistemas

Este documento acompaña a los reportes de ventas (RF07: ventas por período, vendedor y producto). Las consultas están en `ventas/reportes.py` y la pantalla en *Ventas → Reportes de ventas*.

## 1. Qué muestra

La pantalla tiene un filtro de **período** (por defecto, el mes en curso), **sucursal** y **vendedor**, y tres vistas:

| Vista | Contenido |
|---|---|
| **Resumen** | Cantidad de ventas, total vendido, descuentos, ticket promedio y saldo por cobrar. Lo cobrado en el período por forma de pago (efectivo, QR, tarjeta). Ventas anuladas aparte. Ventas por día con una barra proporcional |
| **Por vendedor** | Ventas, total, descuentos, ticket promedio y saldo pendiente de cada vendedor, de mayor a menor |
| **Por producto** | Unidades vendidas e importe de cada artículo y servicio. Con permiso para ver costos, también el costo y el margen en bolivianos y en porcentaje |

Cada vista se exporta a CSV (separado por punto y coma, con coma decimal, para Excel en español) y se puede imprimir.

## 2. Reglas

- **Ventas del período:** son las ventas **vigentes** registradas entre las dos fechas, en días completos y en la hora de Bolivia. Las **anuladas** no suman en ningún total y se informan aparte en el resumen.
- **Cobrado en el período:** los pagos recibidos entre las dos fechas, aunque la venta sea anterior (por ejemplo, el saldo cobrado al entregar). No se cuentan los pagos de ventas anuladas, porque se devolvieron.
- **Saldo por cobrar:** lo que todavía deben las ventas del período.
- **Importe por producto:** a precio de lista. El descuento es de la venta completa y no se reparte entre los artículos; por eso el total por producto puede superar el total vendido.
- **Costo y margen:** el costo es el costo promedio de cada unidad al momento de vender, guardado en la línea de la venta. Los servicios no tienen costo. Solo se muestran a quien tiene `inventario.ver_kardex`.
- **Ventas antiguas:** las registradas antes del módulo de inventario no tienen artículos. Cuentan en el resumen y por vendedor, pero no por producto; la pantalla indica cuántas son.

## 3. Permisos

Los reportes los ven quienes tienen `ventas.ver_todas_ventas`: el **Gerente** y el **Administrador**. Ambos tienen además `inventario.ver_kardex`, así que ven el costo y el margen. Un cajero/vendedor sigue viendo solo sus propias ventas en *Ventas → Mis ventas*.

## 4. Pruebas

```bash
.venv/Scripts/python manage.py test ventas.tests_reportes
```

`ventas/tests_reportes.py` cubre:

- los totales del resumen, con una venta anulada excluida;
- los cobros por forma de pago;
- el ticket promedio, el saldo y las ventas por día;
- los filtros por sucursal, vendedor y período;
- el reporte por vendedor y por producto, con costo y margen;
- la exportación a CSV;
- la validación de fechas;
- el aviso de ventas sin artículos;
- que un cajero no pueda ver los reportes.

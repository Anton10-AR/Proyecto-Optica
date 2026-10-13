# Identidad visual · Ópticas Casimiro

La interfaz busca transmitir una imagen **clínica y confiable**: colores asociados con la salud visual y la precisión, con fondos claros y un único color de acento. Toda la definición está en `static/css/casimiro.css`, que ajusta Bootstrap 5.3 mediante sus variables CSS, sin compilar.

## Paleta

| Uso | Nombre | Hex | Variable CSS |
|---|---|---|---|
| Primario: navegación, botones, títulos | Azul petróleo | `#0F4C5C` | `--oc-petroleo` |
| Hover y estados activos | Petróleo oscuro | `#0A3540` | `--oc-petroleo-oscuro` |
| Fondos de énfasis suave | Petróleo claro | `#E6EFF1` | `--oc-petroleo-claro` |
| Acento decorativo: íconos, bordes, foco | Turquesa | `#2A9D8F` | `--oc-turquesa` |
| Acento sobre texto y botones | Turquesa texto | `#1E7A70` | `--oc-turquesa-texto` |
| Fondo de página | Gris clínico | `#F4F7F8` | `--oc-fondo` |
| Bordes | Gris borde | `#DDE5E8` | `--oc-borde` |
| Texto principal | Grafito | `#1B2B30` | `--oc-texto` |
| Texto secundario | Gris pizarra | `#5B6B70` | `--oc-texto-suave` |
| Éxito: activo, cuadra, pagado | Verde | `#2E7D5B` | `--oc-exito` |
| Aviso: saldo pendiente, caja abierta | Ámbar | `#B7791F` | `--oc-aviso` |
| Error: inactivo, falta, intento fallido | Rojo | `#C2413A` | `--oc-peligro` |

El turquesa claro `#2A9D8F` no tiene contraste suficiente con texto blanco (WCAG AA). Por eso los botones y los enlaces usan `#1E7A70`, y el turquesa claro queda solo para íconos, bordes y el anillo de foco.

## Tipografía e íconos

- **Inter** (pesos 400, 500, 600 y 700) para toda la interfaz. Es legible en tamaños pequeños y tiene números tabulares, como los del reloj de marcación.
- **Bootstrap Icons** para los íconos: navegación, botones y estados vacíos.
- Ambos se sirven desde `static/vendor/`, así que el sistema funciona sin internet.

## Logo

`static/img/logo.svg`: unos anteojos de trazo blanco con reflejos turquesa, sobre un cuadrado redondeado azul petróleo. Se usa en la barra de navegación, en el inicio de sesión, en la nota de venta y como ícono de la pestaña del navegador.

## Componentes propios

| Clase | Uso |
|---|---|
| `.oc-encabezado` | Encabezado de cada pantalla: ícono, título, descripción y acción principal |
| `.oc-indicador` | Tarjeta de cifra con ícono, por ejemplo en el inicio o el arqueo de caja |
| `.oc-acceso` | Tarjeta de acceso rápido que se eleva al pasar el cursor |
| `.oc-estado-ok`, `-aviso`, `-peligro`, `-inactivo` | Insignias de estado con punto de color |
| `.btn-acento` | Botón turquesa para acciones secundarias destacadas, como marcar la salida |
| `.oc-marcar`, `.oc-reloj` | Botón grande y reloj de la pantalla de marcación |

Las pantallas siguen siempre el mismo patrón:

- encabezado con ícono;
- filtros dentro de una tarjeta;
- tablas en tarjetas, con cabecera en mayúsculas pequeñas;
- botón principal en azul petróleo arriba a la derecha.

Los menús se arman según los permisos del usuario, así que cada rol solo ve lo que puede usar.

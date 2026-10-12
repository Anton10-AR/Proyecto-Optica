const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, LevelFormat, PageBreak, Footer, Header, PageNumber,
  TableOfContents,
} = require('docx');

const OUT = process.argv[2];
const FONT = 'Arial';
const CONTENT_W = 9026; // A4 con márgenes de 1"

// ---------- helpers ----------
const runs = (text, opts = {}) => {
  // Soporta **negrita** dentro del texto
  const parts = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map(p => p.startsWith('**')
    ? new TextRun({ text: p.slice(2, -2), bold: true, ...opts })
    : new TextRun({ text: p, ...opts }));
};
const P = (text, opts = {}) => new Paragraph({
  children: runs(text), spacing: { after: 120, line: 300 }, alignment: AlignmentType.JUSTIFIED, ...opts,
});
const H1 = text => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
const H2 = text => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
const H3 = text => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(text)] });
const B = (text, level = 0) => new Paragraph({
  numbering: { reference: 'bullets', level }, children: runs(text), spacing: { after: 60, line: 288 },
});
const REQ = (code, text) => new Paragraph({
  children: [new TextRun({ text: code + '. ', bold: true }), ...runs(text)],
  spacing: { after: 100, line: 288 }, alignment: AlignmentType.JUSTIFIED, indent: { left: 0 },
});

const border = { style: BorderStyle.SINGLE, size: 4, color: '8C8C8C' };
const borders = { top: border, bottom: border, left: border, right: border };
const cell = (text, width, header = false) => new TableCell({
  borders, width: { size: width, type: WidthType.DXA },
  shading: header ? { fill: '1F4E79', type: ShadingType.CLEAR, color: 'auto' } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: [new Paragraph({
    children: runs(text, header ? { bold: true, color: 'FFFFFF' } : {}),
    spacing: { after: 0, line: 264 },
  })],
});
const T = (widths, header, rows) => new Table({
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  columnWidths: widths,
  rows: [
    new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, widths[i], true)) }),
    ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, widths[i])) })),
  ],
});
const gap = () => new Paragraph({ children: [], spacing: { after: 120 } });
const boxBorder = { style: BorderStyle.SINGLE, size: 6, color: '1F4E79', space: 6 };
const box = text => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 120, after: 120 },
  keepNext: true,
  border: { top: boxBorder, bottom: boxBorder, left: boxBorder, right: boxBorder },
  shading: { fill: 'DEEAF6', type: ShadingType.CLEAR, color: 'auto' },
  indent: { left: 1300, right: 1300 },
  children: runs(text),
});
const arrow = label => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 0 }, keepNext: true,
  children: [new TextRun({ text: '▼  ' + label, color: '1F4E79' })],
});
const center = (text, size, bold = false, after = 120, italics = false) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after },
  children: [new TextRun({ text, size, bold, italics })],
});

// ---------- portada ----------
const portada = [
  center('UNIVERSIDAD MAYOR REAL Y PONTIFICIA', 28, true, 0),
  center('SAN FRANCISCO XAVIER DE CHUQUISACA', 28, true, 240),
  center('FACULTAD DE CIENCIAS Y TECNOLOGÍA', 24, true, 1200),
  center('VISIÓN DEL PROYECTO', 40, true, 360),
  center('ÓPTICAS CASIMIRO', 36, true, 120),
  center('Cuidando cada detalle de tu visión', 24, false, 240, true),
  center('Sistema Informático de Ventas, Almacenes/Inventario y Control de Asistencia', 24, false, 1200),
  center('ESTUDIANTES:', 24, true, 60),
  center('Aguilar Rosales Carla Fátima', 24, false, 0),
  center('Avendaño Retamozo Juan Antonio', 24, false, 0),
  center('Cueto Chavez Abigail Fernanda', 24, false, 360),
  center('DOCENTE: Ing. Ramiro Durán', 24, true, 360),
  center('MATERIA: SIS301 Análisis y Diseño de Sistemas', 24, false, 1200),
  center('Sucre – Bolivia', 24, false, 0),
  center('2026', 24, false, 0),
  new Paragraph({ children: [new PageBreak()] }),
  new Paragraph({ children: [new TextRun({ text: 'Índice', bold: true, size: 32 })], spacing: { after: 240 } }),
  new TableOfContents('Índice', { hyperlink: true, headingStyleRange: '1-3' }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ---------- 1. Introducción ----------
const intro = [
  H1('1. Introducción'),
  H2('1.1 Nombre del proyecto'),
  P('Ópticas Casimiro – Sistema Informático de Ventas, Almacenes/Inventario y Control de Asistencia. El proyecto está orientado al desarrollo de un sistema informático integrado para una óptica, que permita gestionar la venta de productos ópticos, incluidas las recetas de los clientes y las órdenes de trabajo del taller, controlar el inventario de mercadería de cada sucursal y registrar la asistencia del personal.'),
  H2('1.2 Propósito del documento'),
  P('El presente documento describe la visión general del sistema de "Ópticas Casimiro": sus objetivos, alcance, oportunidad de negocio, partes interesadas, usuarios y características principales. También establece los requisitos de alto nivel y la arquitectura general necesarios para orientar el análisis, diseño y desarrollo del sistema.'),
  H2('1.3 Alcance'),
  P('La primera versión del sistema de "Ópticas Casimiro" integrará tres procesos principales de la operación de la óptica (ventas, almacenes/inventario y control de asistencia del personal) junto con la administración de usuarios y roles:'),
  B('Registro de clientes y de sus recetas oftalmológicas, tanto de exámenes realizados en la óptica como de recetas externas.'),
  B('Registro de ventas de armazones, lunas/cristales, lentes de contacto y accesorios, con pagos parciales (anticipo y saldo).'),
  B('Generación de órdenes de trabajo para el taller propio y seguimiento de su estado hasta la entrega al cliente.'),
  B('Emisión de comprobante de venta (nota de venta no fiscal) y consulta de stock disponible.'),
  B('Apertura, movimientos y cierre de caja con arqueo, por usuario y sucursal.'),
  B('Registro de artículos, ingresos, salidas, traspasos entre sucursales y kardex valorado de inventario por sucursal.'),
  B('Gestión de proveedores y alertas de stock mínimo.'),
  B('Registro de entrada y salida del personal por sucursal, validado mediante geolocalización.'),
  B('Gestión de empleados, sucursales, horarios (incluido el horario partido), permisos, vacaciones, feriados y configuración de tolerancia.'),
  B('Gestión de usuarios, roles y acceso al sistema.'),
  B('Reportes de ventas, inventario y asistencia.'),
  P('Fuera del alcance de la primera versión:'),
  B('Aplicación móvil nativa (el personal marcará su asistencia desde el navegador del celular).'),
  B('Facturación electrónica ante el Servicio de Impuestos Nacionales (SIN).'),
  B('Gestión de nómina/planillas de sueldos.'),
  B('Contabilidad general de la empresa.'),
  B('Envío de trabajos a laboratorios externos.'),
  H2('1.4 Definiciones y acrónimos'),
  T([2600, 6426], ['Término', 'Definición'], [
    ['Anticipo', 'Pago parcial que realiza el cliente al registrar la venta; el resto (saldo) se paga a la entrega.'],
    ['Arqueo de caja', 'Conteo del efectivo al cerrar la caja y comparación con el monto que el sistema calcula como esperado.'],
    ['Armazón', 'Montura de anteojos que sostiene las lunas o cristales.'],
    ['Costo promedio ponderado', 'Método de valoración del inventario en el que cada ingreso recalcula el costo unitario promedio del artículo; las salidas se valoran a ese costo.'],
    ['Distancia pupilar (DP)', 'Distancia, en milímetros, entre los centros de las pupilas; se usa para centrar las lunas en el armazón.'],
    ['Esfera, cilindro, eje y adición', 'Parámetros de la graduación de cada ojo: la esfera corrige la miopía o hipermetropía, el cilindro y el eje corrigen el astigmatismo, y la adición es la potencia adicional para visión cercana.'],
    ['Geolocalización', 'Ubicación geográfica del dispositivo, obtenida por el navegador, que se usa para validar que el empleado marca su asistencia en la sucursal.'],
    ['Horario partido', 'Jornada laboral dividida en dos o más tramos en un mismo día (por ejemplo, mañana y tarde).'],
    ['Kardex', 'Registro histórico de entradas y salidas de un artículo en almacén.'],
    ['Luna / Cristal', 'Lente graduado o no graduado que se coloca en el armazón.'],
    ['Nota de venta', 'Comprobante de venta no fiscal emitido por el sistema.'],
    ['OD / OI', 'Ojo derecho / ojo izquierdo.'],
    ['Orden de trabajo', 'Solicitud al taller para armar los lentes graduados de una venta, según la receta del cliente.'],
    ['Receta oftalmológica', 'Documento con la graduación de cada ojo del cliente, emitido tras un examen visual.'],
    ['Saldo', 'Monto pendiente de pago de una venta.'],
    ['Sucursal', 'Punto de atención de la óptica donde presta funciones el personal.'],
    ['Tolerancia', 'Margen de minutos permitido antes de registrar un atraso.'],
    ['Traspaso', 'Movimiento de mercadería de una sucursal a otra.'],
    ['HTTPS', 'Protocolo de comunicación web cifrado.'],
    ['MVT', 'Modelo–Vista–Plantilla, patrón de arquitectura del framework Django.'],
    ['RF', 'Requisito funcional.'],
    ['RNF', 'Requisito no funcional.'],
    ['SIN', 'Servicio de Impuestos Nacionales de Bolivia.'],
  ]),
  H2('1.5 Referencias'),
  B('Durán, R. Visión del proyecto (plantilla). SIS301 Análisis y Diseño de Sistemas, Universidad Mayor Real y Pontificia de San Francisco Xavier de Chuquisaca, 2026.'),
  B('Entrevistas con la gerencia de Ópticas Casimiro. [Completar con fechas y personas entrevistadas.]'),
  B('Django Software Foundation. Django 6.1 Documentation. https://docs.djangoproject.com/'),
  B('The PostgreSQL Global Development Group. PostgreSQL 18 Documentation. https://www.postgresql.org/docs/'),
];

// ---------- 2. Posicionamiento ----------
const posicionamiento = [
  H1('2. Posicionamiento del negocio'),
  H2('2.1 Oportunidad de negocio'),
  P('"Ópticas Casimiro" ha experimentado un crecimiento sostenido en el número de clientes y en la variedad de productos que ofrece, lo que ha vuelto poco práctico el control manual de ventas, existencias y asistencia del personal mediante planillas físicas y hojas de cálculo aisladas. Un sistema informático integrado permitiría reducir errores, agilizar la atención al cliente y disponer de información oportuna para la toma de decisiones.'),
  H2('2.2 Declaración del problema'),
  T([2600, 6426], ['Elemento', 'Descripción'], [
    ['El problema de', 'la falta de un sistema integrado que gestione de forma centralizada las ventas, el inventario y la asistencia del personal en "Ópticas Casimiro"'],
    ['Afecta a', 'los vendedores, el personal del taller, el encargado de almacén, el personal administrativo y la gerencia de la óptica'],
    ['El impacto del problema es', 'demoras en la atención al cliente, pérdida de seguimiento de los trabajos del taller, descuadres de inventario y dificultad para controlar la puntualidad del personal'],
    ['Una solución exitosa sería', 'un sistema que integre Ventas, Almacenes/Inventario y Control de Asistencia, con información en tiempo real y reportes confiables'],
  ]),
  H2('2.3 Declaración de la posición del producto'),
  P('Para la gerencia y el personal de "Ópticas Casimiro" que necesitan gestionar de manera eficiente las ventas, el inventario y la asistencia de sus colaboradores, el Sistema Informático Ópticas Casimiro es una plataforma web integrada que permite registrar ventas con sus recetas y órdenes de trabajo, controlar existencias por sucursal y registrar la asistencia del personal. A diferencia de los registros manuales o en hojas de cálculo actualmente utilizados, el sistema centraliza la información del negocio y reduce el tiempo de atención y control.'),
];

// ---------- 3. Partes interesadas y usuarios ----------
const perfil = (nombre, resp, obj, prob, exito) => [
  new Paragraph({
    keepNext: true, spacing: { before: 200, after: 80 },
    children: [new TextRun({ text: nombre, bold: true, color: '1F4E79' })],
  }),
  B('**Responsabilidades en el sistema:** ' + resp),
  B('**Objetivos:** ' + obj),
  B('**Problemas actuales:** ' + prob),
  B('**Criterio de éxito:** ' + exito),
];
const partes = [
  H1('3. Partes interesadas y usuarios'),
  H2('3.1 Resumen de las partes interesadas'),
  T([3000, 6026], ['Parte interesada', 'Interés o función'], [
    ['Gerente propietario', 'Supervisar el negocio, aprobar requisitos y validar los entregables.'],
    ['Administrador del sistema', 'Configurar, mantener y administrar el sistema una vez implementado.'],
    ['Docente de la materia', 'Guía metodológica y evaluador del proyecto.'],
    ['Equipo de desarrollo', 'Analizar, diseñar, desarrollar y documentar el sistema.'],
  ]),
  H2('3.2 Resumen de los usuarios'),
  B('**Cajero/Vendedor:** atiende a los clientes, registra sus datos y recetas externas, registra las ventas y los pagos, opera su caja (apertura, movimientos y cierre), consulta el stock disponible y entrega los trabajos terminados.'),
  B('**Óptico / técnico de taller:** realiza los exámenes visuales en la óptica, registra la receta resultante y actualiza el estado de las órdenes de trabajo.'),
  B('**Encargado de almacén:** registra el ingreso, salida y traspaso de mercadería, controla el nivel de existencias de cada sucursal y gestiona proveedores.'),
  B('**Encargado de Recursos Humanos:** gestiona empleados, sucursales, horarios, permisos, vacaciones, feriados y tolerancias, y supervisa los reportes de asistencia.'),
  B('**Empleado** (óptico, vendedor, personal administrativo): registra su propia entrada y salida desde el navegador de su celular.'),
  B('**Gerente:** consulta reportes de ventas, inventario y asistencia, autoriza entregas con saldo pendiente y define los parámetros del negocio.'),
  B('**Administrador del sistema:** gestiona los usuarios y sus roles.'),
  H2('3.3 Entorno del usuario'),
  P('El sistema será una aplicación web utilizada en los puntos de venta, el taller y el almacén de cada sucursal de "Ópticas Casimiro", desde computadoras con acceso a la red. El personal registrará su asistencia desde el navegador de su celular, que deberá contar con GPS para validar su ubicación. La óptica trabaja con horario partido (mañana y tarde), por lo que una jornada laboral puede tener varios tramos en un mismo día.'),
  H2('3.4 Perfiles de las partes interesadas y de los usuarios'),
  ...perfil('Gerente propietario',
    'consulta reportes, autoriza entregas con saldo pendiente y define parámetros como la tolerancia y el anticipo mínimo.',
    'conocer las ventas, los márgenes y el desempeño del personal de cada sucursal.',
    'la información está dispersa en planillas y hojas de cálculo, y no dispone de datos oportunos para tomar decisiones.',
    'obtiene reportes confiables de cualquier sucursal sin solicitarlos manualmente.'),
  ...perfil('Cajero/Vendedor',
    'registra clientes, recetas externas, ventas y pagos; abre, opera y cierra su caja; entrega los trabajos terminados.',
    'atender rápido y sin errores.',
    'consulta manualmente el stock y el estado de los pedidos, y comete errores en los cálculos.',
    'registra una venta completa en menos de 3 minutos (RNF01).'),
  ...perfil('Óptico / técnico de taller',
    'realiza exámenes visuales y actualiza el estado de las órdenes de trabajo.',
    'armar cada trabajo con la graduación correcta y a tiempo.',
    'las órdenes se pierden o no se conoce su estado.',
    'cada orden tiene su receta asociada y un estado visible para todo el personal.'),
  ...perfil('Encargado de almacén',
    'registra ingresos, salidas y traspasos; gestiona proveedores.',
    'mantener el stock correcto en cada sucursal.',
    'existen descuadres de inventario y no sabe con certeza qué reponer.',
    'el kardex coincide con el conteo físico y recibe alertas de stock mínimo.'),
  ...perfil('Encargado de Recursos Humanos',
    'gestiona empleados, horarios, permisos, vacaciones y feriados; revisa los reportes de asistencia.',
    'controlar la puntualidad del personal de forma justa.',
    'las planillas físicas de asistencia son difíciles de consolidar y verificar.',
    'los atrasos y faltas se calculan automáticamente, descontando permisos, vacaciones y feriados.'),
  ...perfil('Empleado',
    'marca su entrada y salida desde el celular.',
    'registrar su asistencia sin trámites.',
    'el registro manual es lento y propenso a errores.',
    'marca su asistencia en segundos y solo dentro de su sucursal.'),
  ...perfil('Administrador del sistema',
    'gestiona usuarios y roles; mantiene el sistema en funcionamiento.',
    'que cada usuario acceda solo a la información que le corresponde.',
    'actualmente no existe un control de acceso a la información.',
    'los roles y permisos se configuran sin modificar el código del sistema.'),
];

// ---------- 4. Características y requisitos ----------
const caracteristicas = [
  H1('4. Características del producto'),
  H2('4.1 Módulo de Ventas'),
  B('Registro y consulta de clientes.'),
  B('Registro de recetas oftalmológicas (examen en la óptica o receta externa) e historial por cliente.'),
  B('Registro de ventas seleccionando cliente, productos y cantidades.'),
  B('Cálculo automático de subtotales, descuentos y total a pagar.'),
  B('Registro de pagos parciales (anticipo y saldo) con su forma de pago, y control de un anticipo mínimo para lentes graduados.'),
  B('Generación de órdenes de trabajo para el taller y seguimiento de su estado.'),
  B('Control de entrega: no se entregan trabajos con saldo pendiente sin autorización del gerente.'),
  B('Emisión de comprobante de venta (nota de venta no fiscal), con el vendedor en el encabezado.'),
  B('Caja: apertura con monto inicial, registro de ingresos y egresos, y cierre con arqueo de efectivo.'),
  B('Consulta de stock disponible al momento de la venta.'),
  B('Anulación de ventas con reversión del stock.'),
  B('Reporte de ventas por período, vendedor y producto.'),
  H2('4.2 Módulo de Almacenes/Inventario'),
  B('Registro de artículos con sus atributos (código, categoría, proveedor, stock mínimo).'),
  B('Control de existencias por sucursal.'),
  B('Registro de ingresos de mercadería por compra a proveedores.'),
  B('Registro de salidas por ventas, bajas o traspasos entre sucursales.'),
  B('Kardex de movimientos por artículo y sucursal, valorado por costo promedio ponderado.'),
  B('Alertas de stock mínimo.'),
  B('Gestión de proveedores.'),
  B('Reporte de existencias e inventario.'),
  H2('4.3 Módulo de Control de Asistencia'),
  B('Gestión de empleados.'),
  B('Registro de entrada y salida del personal por sucursal, validado por geolocalización.'),
  B('Gestión de sucursales de la óptica, con su ubicación y radio de marcación.'),
  B('Gestión de horarios laborales por empleado, incluido el horario partido.'),
  B('Registro de permisos y vacaciones, y calendario de feriados.'),
  B('Configuración de tolerancia y otros parámetros del sistema.'),
  B('Cálculo automático de atrasos, faltas y horas trabajadas.'),
  B('Reporte de asistencia, atrasos y faltas por empleado, sucursal y período.'),
  H2('4.4 Administración del sistema'),
  B('Gestión de usuarios y asignación de roles, con baja lógica.'),
  B('Registro de actividad (auditoría) de las acciones de seguridad.'),
  B('Inicio y cierre de sesión.'),
  B('Restricción del acceso a cada módulo según el rol del usuario.'),

  H2('4.5 Requisitos del sistema'),
  H3('4.5.1 Requisitos funcionales'),
  P('**Módulo de Ventas**'),
  REQ('RF01', 'El sistema deberá permitir registrar nuevas ventas seleccionando cliente, productos y cantidades.'),
  REQ('RF02', 'El sistema deberá calcular automáticamente subtotales, descuentos y el total a pagar.'),
  REQ('RF03', 'El sistema deberá permitir emitir el comprobante de venta (nota de venta no fiscal).'),
  REQ('RF04', 'El sistema deberá permitir consultar el stock disponible al momento de la venta.'),
  REQ('RF05', 'El sistema deberá permitir registrar y consultar los datos básicos del cliente.'),
  REQ('RF06', 'El sistema deberá permitir anular una venta y revertir el stock correspondiente.'),
  REQ('RF07', 'El sistema deberá generar reportes de ventas por período, vendedor y producto.'),
  REQ('RF21', 'El sistema deberá permitir registrar la receta oftalmológica del cliente: graduación de cada ojo (OD/OI: esfera, cilindro, eje y adición), distancia pupilar, fecha y origen. El origen puede ser un examen realizado en la óptica, con el óptico responsable, o una receta externa, con el médico o la institución que la emitió.'),
  REQ('RF22', 'El sistema deberá permitir consultar el historial de recetas de cada cliente.'),
  REQ('RF23', 'El sistema deberá generar una orden de trabajo para el taller al registrar una venta de lentes graduados, asociada a la receta del cliente.'),
  REQ('RF24', 'El sistema deberá permitir actualizar el estado de las órdenes de trabajo (pendiente, en taller, listo, entregado) y consultarlas por estado.'),
  REQ('RF25', 'El sistema deberá permitir registrar uno o más pagos por venta (anticipo y saldo), cada uno con su forma de pago (efectivo, QR o tarjeta), e informar el saldo pendiente. Cada pago se registra como ingreso en la caja abierta del usuario que lo cobra.'),
  REQ('RF31', 'El sistema deberá impedir que una orden de trabajo se marque como entregada mientras la venta tenga saldo pendiente, salvo autorización del gerente, que quedará registrada.'),
  REQ('RF32', 'El sistema deberá exigir un anticipo mínimo, configurable como porcentaje, al registrar una venta de lentes graduados.'),
  REQ('RF33', 'El sistema deberá permitir a cada cajero/vendedor abrir su caja con un monto inicial, vinculada a su usuario y sucursal, y no permitirá más de una caja abierta por usuario.'),
  REQ('RF34', 'El sistema deberá permitir registrar ingresos y egresos de caja con su forma de pago y concepto, y exigirá una caja abierta para registrar ventas y pagos.'),
  REQ('RF35', 'El sistema deberá permitir cerrar la caja registrando el efectivo contado (arqueo) y calcular la diferencia con el efectivo esperado.'),
  P('**Módulo de Almacenes/Inventario**'),
  REQ('RF08', 'El sistema deberá permitir registrar los artículos del inventario con sus atributos (código, categoría, proveedor, stock mínimo) y controlar sus existencias por sucursal.'),
  REQ('RF09', 'El sistema deberá permitir registrar los ingresos de mercadería por compra a proveedores.'),
  REQ('RF10', 'El sistema deberá permitir registrar las salidas de mercadería por ventas, bajas o traspasos entre sucursales. Un traspaso registra la salida en la sucursal de origen y el ingreso en la de destino.'),
  REQ('RF11', 'El sistema deberá mantener un kardex de movimientos por artículo y sucursal, valorado por el método de costo promedio ponderado.'),
  REQ('RF12', 'El sistema deberá generar alertas cuando un artículo alcance su stock mínimo en una sucursal.'),
  REQ('RF13', 'El sistema deberá permitir gestionar la información de los proveedores.'),
  REQ('RF14', 'El sistema deberá generar reportes de existencias e inventario valorado, por sucursal y consolidados.'),
  P('**Módulo de Control de Asistencia**'),
  REQ('RF15', 'El sistema deberá permitir registrar la entrada y salida del personal por sucursal, validando mediante geolocalización que el empleado se encuentra dentro del radio permitido de la sucursal.'),
  REQ('RF16', 'El sistema deberá permitir gestionar las sucursales de la óptica, incluyendo su ubicación geográfica y el radio permitido para la marcación.'),
  REQ('RF17', 'El sistema deberá permitir gestionar los horarios laborales asignados a cada empleado, admitiendo varios tramos por día (horario partido).'),
  REQ('RF18', 'El sistema deberá permitir configurar la tolerancia y otros parámetros del control de asistencia.'),
  REQ('RF19', 'El sistema deberá calcular automáticamente atrasos, faltas y horas trabajadas, considerando cada tramo del horario y excluyendo permisos, vacaciones y feriados.'),
  REQ('RF20', 'El sistema deberá generar reportes de asistencia, atrasos y faltas por empleado, sucursal y período.'),
  REQ('RF26', 'El sistema deberá permitir gestionar los datos de los empleados: datos personales, cargo y sucursal asignada.'),
  REQ('RF27', 'El sistema deberá permitir registrar permisos y vacaciones por empleado, que no se computarán como faltas.'),
  REQ('RF28', 'El sistema deberá permitir gestionar un calendario de feriados, que no se computarán como faltas.'),
  P('**Administración del sistema**'),
  REQ('RF29', 'El sistema deberá permitir gestionar los usuarios y asignarles un rol (administrador, gerente, cajero/vendedor, recursos humanos, encargado de almacén, óptico/técnico de taller, empleado), así como desactivar cuentas sin eliminar su historial (baja lógica).'),
  REQ('RF30', 'El sistema deberá exigir que el usuario inicie sesión con su usuario o correo y su contraseña antes de acceder a cualquier módulo.'),
  REQ('RF36', 'El sistema deberá registrar en un log de actividad la fecha, hora y usuario de los inicios de sesión, intentos fallidos, cambios de contraseña y creación o desactivación de cuentas.'),

  H3('4.5.2 Requisitos no funcionales'),
  REQ('RNF01', '**Usabilidad:** un vendedor deberá poder registrar una venta completa en menos de 3 minutos tras una capacitación de 1 hora.'),
  REQ('RNF02', '**Rendimiento:** las operaciones de venta, inventario y asistencia deberán responder en menos de 2 segundos con hasta 10 usuarios simultáneos.'),
  REQ('RNF03', '**Seguridad:** el acceso a cada módulo deberá estar restringido según el rol del usuario. Las contraseñas se almacenarán cifradas con Argon2 y las sesiones expirarán tras 30 minutos de inactividad.'),
  REQ('RNF04', '**Disponibilidad:** el sistema deberá estar disponible durante todo el horario de atención de cada sucursal, con una disponibilidad mínima del 99 % en ese horario.'),
  REQ('RNF05', '**Fiabilidad:** el descuento de stock tras una venta y su registro en el kardex deberán realizarse en una misma transacción, de modo que se reflejen de forma inmediata y consistente en el inventario.'),
  REQ('RNF06', '**Mantenibilidad:** el sistema deberá estar organizado en módulos independientes que faciliten futuras ampliaciones.'),
  REQ('RNF07', '**Compatibilidad:** el sistema deberá funcionar en las versiones actuales de Chrome, Edge y Firefox, tanto en computadoras como en celulares Android e iOS.'),
  REQ('RNF08', '**Requisitos del sistema:** se requiere una computadora con acceso a la red en cada punto de venta, taller y almacén. El sistema deberá publicarse con HTTPS, ya que los navegadores solo permiten la geolocalización en conexiones seguras.'),

  H2('4.6 Restricciones'),
  B('Tiempo limitado de desarrollo según el cronograma académico.'),
  B('Presupuesto y recursos tecnológicos limitados, propios del entorno académico; el sistema se construirá con herramientas de software libre (Django, PostgreSQL).'),
  B('El proyecto está orientado a una sola empresa (Ópticas Casimiro) y sus sucursales, sin contemplar varias empresas.'),
  B('La marcación de asistencia por geolocalización requiere que el sistema se publique con HTTPS y que el dispositivo del empleado cuente con GPS.'),
  B('Las funciones avanzadas podrán incorporarse en versiones posteriores.'),
];

// ---------- 5. Arquitectura ----------
const arquitectura = [
  H1('5. Arquitectura del sistema'),
  P('El sistema se desarrollará como una **aplicación web** con arquitectura de **monolito modular**, sobre el framework **Django** (Python) y el patrón **MVT** (Modelo–Vista–Plantilla). Todos los módulos comparten una única base de datos **PostgreSQL**, lo que garantiza la consistencia de la información entre ventas, inventario y asistencia.'),
  P('Cada módulo del sistema es una aplicación Django independiente (RNF06):'),
  T([3200, 2400, 3426], ['Módulo', 'Aplicación Django', 'Depende de'], [
    ['Administración del sistema', 'core', '—'],
    ['Almacenes/Inventario', 'inventario', 'core'],
    ['Caja', 'caja', 'core'],
    ['Ventas', 'ventas', 'core, inventario, caja'],
    ['Control de asistencia', 'asistencia', 'core'],
  ]),
  gap(),
  B('**Presentación:** plantillas HTML responsivas con HTMX para la interactividad; funcionan en las computadoras de la óptica y en los celulares del personal sin instalar una aplicación (RNF07).'),
  B('**Seguridad:** autenticación y permisos de Django; cada rol es un grupo con permisos sobre los módulos que le corresponden (RNF03, RF29, RF30).'),
  B('**Consistencia del stock:** toda operación que mueve mercadería actualiza las existencias y el kardex en una única transacción de base de datos, de modo que una venta nunca queda registrada sin su descuento de stock (RNF05).'),
  B('**Despliegue:** un servidor web con HTTPS, accesible desde la red de cada sucursal (RNF08).'),
  gap(),
  box('**Navegador** (computadora / celular)'),
  arrow('HTTPS'),
  box('**Servidor Django**: core · inventario · caja · ventas · asistencia'),
  arrow('SQL'),
  box('**PostgreSQL** (base de datos única)'),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120, after: 240 },
    children: [new TextRun({ text: 'Figura 1. Arquitectura general del sistema.', italics: true, size: 20 })],
  }),
];

// ---------- 6-8 ----------
const cierre = [
  H1('6. Objetivo general'),
  P('Desarrollar un sistema informático integrado para "Ópticas Casimiro" que permita gestionar los procesos de ventas, control de inventario y control de asistencia del personal, mejorando la eficiencia operativa y la disponibilidad de información para la toma de decisiones.'),
  H1('7. Objetivos específicos'),
  B('Diseñar un módulo de ventas que permita registrar y controlar las transacciones comerciales de la óptica, incluidas las recetas de los clientes, las órdenes de trabajo del taller y los pagos.'),
  B('Implementar un módulo de almacén e inventario que mantenga actualizado el stock de productos ópticos de cada sucursal.'),
  B('Desarrollar un módulo de control de asistencia que registre la entrada, salida y puntualidad del personal.'),
  B('Integrar los tres módulos sobre una base de datos común para mantener la consistencia de la información.'),
  B('Generar reportes que apoyen la toma de decisiones de la gerencia.'),
  H1('8. Conclusión'),
  P('"Ópticas Casimiro" propone una solución informática integral para optimizar la gestión de ventas, el control de inventario y la asistencia del personal de la óptica. La integración de estos tres módulos sobre una base de datos común permitirá contar con información actualizada y confiable para la operación diaria y la toma de decisiones gerenciales. Este documento de Visión servirá como base para las siguientes etapas de análisis, diseño de casos de uso, modelado de datos e implementación del sistema.'),
];

// ---------- documento ----------
const doc = new Document({
  creator: 'Equipo Ópticas Casimiro',
  title: 'Visión del Proyecto – Ópticas Casimiro',
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 30, bold: true, font: FONT, color: '1F4E79' },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0, keepNext: true, keepLines: true } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 25, bold: true, font: FONT, color: '1F4E79' },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1, keepNext: true, keepLines: true } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 23, bold: true, font: FONT, color: '2E2E2E' },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2, keepNext: true, keepLines: true } },
    ],
  },
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
    }],
  },
  sections: [
    {
      properties: { page: { size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      children: portada,
    },
    {
      properties: { page: { size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }, pageNumbers: { start: 1 } } },
      headers: { default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: 'Visión del Proyecto – Ópticas Casimiro', size: 18, color: '7F7F7F' })],
      })] }) },
      footers: { default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: [PageNumber.CURRENT], size: 18 })],
      })] }) },
      children: [...intro, ...posicionamiento, ...partes, ...caracteristicas, ...arquitectura, ...cierre],
    },
  ],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log('OK', OUT, buf.length); });

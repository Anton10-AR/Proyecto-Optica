-- Ópticas Casimiro · Datos de prueba (seeds)
-- Generado con pg_dump a partir de `manage.py cargar_datos_prueba` sobre una base recién migrada.
-- Incluye roles y permisos, sucursales, usuarios, una caja y una venta de ejemplo con sus líneas, marcaciones,
-- el catálogo de inventario y sus movimientos iniciales (compras, traspasos y una baja),
-- y clientes con su historial de recetas y una orden de trabajo lista con saldo pendiente.
-- Contraseña de todos los usuarios de prueba: Casimiro2026! (guardada con Argon2).
-- Ejecutar después de 01_esquema.sql sobre una base vacía.
-- La forma recomendada de recrear estos datos es: manage.py migrate && manage.py cargar_datos_prueba

--
-- PostgreSQL database dump
--

\restrict DFHJqZcmGy2IX1FS49juH9HRnvrqZqH4NJspVqVdEYLpCAei0WhUUQIuqRMFbuN

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
1	Administrador
2	Gerente
3	Cajero/Vendedor
4	Recursos Humanos
5	Encargado de almacén
6	Óptico/Técnico de taller
7	Empleado
\.


--
-- Data for Name: core_sucursal; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.core_sucursal (id, nombre, direccion, latitud, longitud, radio_metros, activa) FROM stdin;
1	Sucursal Centro	Dirección de prueba 1, Sucre	-19.039699	-65.256900	300	t
2	Sucursal Norte	Dirección de prueba 2, Sucre	-19.039699	-65.256900	300	t
\.


--
-- Data for Name: core_usuario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) FROM stdin;
1	argon2$argon2id$v=19$m=102400,t=2,p=8$NWd0Z1E5WlA0VDdycVFtYVYxNFlUNQ$jo3FEJWnRBFhexTkotWd1GyKVmLmWpNWfGaITY/V4XE	\N	f	administrador	Sofía	Torrico Lima	administrador@opticascasimiro.test	f	t	2026-11-08 13:52:27.272587-04	1000001	f	1	70000001	1
2	argon2$argon2id$v=19$m=102400,t=2,p=8$RXNyMnVYYzNyQTdVdW9sVFRKdkIyRA$o23ZrC4G371KDdkHFuqDGs7ULrVTy9SfszMwpkB1on4	\N	f	gerente	Daniel	Ortiz Paredes	gerente@opticascasimiro.test	f	t	2026-11-08 13:52:27.451161-04	1000002	f	2	70000002	1
3	argon2$argon2id$v=19$m=102400,t=2,p=8$ejJVV0NISDVuU3RPanpzZVFYVTZCdw$omZsm0fA+33/jmXPf2EAh4xvPWCb6sZtEZ4aXQeSbz4	\N	f	cajero1	Juan	Pérez Mamani	cajero1@opticascasimiro.test	f	t	2026-11-08 13:52:27.504066-04	1000003	f	3	70000003	1
4	argon2$argon2id$v=19$m=102400,t=2,p=8$TGNmZHpvZGc1M2J1cWw0VXUwSE1XMA$ifc38PEPQTrxk+I9JlDY2SKl2On/22guqCC3L6/q858	\N	f	cajero2	Lucía	Quispe Vargas	cajero2@opticascasimiro.test	f	t	2026-11-08 13:52:27.558125-04	1000004	f	3	70000004	2
5	argon2$argon2id$v=19$m=102400,t=2,p=8$UE5JZFczT3dCMTBZM0U4NnJ2WEp0QQ$IhBO5EfRCUd/IDQATQocvWbZ3eREqceumvpC9ORJSmM	\N	f	rrhh	Valeria	Ramos Soliz	rrhh@opticascasimiro.test	f	t	2026-11-08 13:52:27.610059-04	1000005	f	4	70000005	1
6	argon2$argon2id$v=19$m=102400,t=2,p=8$cDJvSFcyUElPVXRuQkpBSXI0bHNYaA$Bmo/pphcgfRnnYtyh0idwy19tE2mQEVEWqOIayBMu74	\N	f	almacen	Pedro	Rojas Torrez	almacen@opticascasimiro.test	f	t	2026-11-08 13:52:27.662926-04	1000006	f	5	70000006	1
7	argon2$argon2id$v=19$m=102400,t=2,p=8$dlhQdEhrZ1RndDBPQlNlWFlVdHdUUg$oh27JjaIcJ5nTBgs3tgeNSnJq4BHBT5iKGimmgSETMU	\N	f	optico	Marta	Gutiérrez Choque	optico@opticascasimiro.test	f	t	2026-11-08 13:52:27.724596-04	1000007	f	6	70000007	1
8	argon2$argon2id$v=19$m=102400,t=2,p=8$dm5hZWloN05JRzlBZUlvVWRzbGg4ag$5RrngUl4Qb+s/RtrfoeYm0QQKX1yZJKxXRGf322wHBM	\N	f	empleado1	Luis	Fernández Cruz	empleado1@opticascasimiro.test	f	t	2026-11-08 13:52:27.782015-04	1000008	f	7	70000008	1
9	argon2$argon2id$v=19$m=102400,t=2,p=8$dFRxZXBCZHp1RFpVRG5RV1B0enJtag$W0bCulqzs1kTQ4f2EU62WKxt/ntItH4OokMvjTnV9TI	\N	f	empleado2	Ana	Mendoza Arce	empleado2@opticascasimiro.test	f	t	2026-11-08 13:52:27.839317-04	1000009	f	7	70000009	2
10	argon2$argon2id$v=19$m=102400,t=2,p=8$UHp1VWpDSUtrdEdaNXNkYXhaWFFudg$P2ma3/jaRREHS82lDXn7LSj4IqG506waTN9s35m3mZw	\N	f	exempleado	Jorge	Salazar Ríos	exempleado@opticascasimiro.test	f	f	2026-11-08 13:52:27.896298-04	1000010	f	7	70000010	1
\.


--
-- Data for Name: asistencia_marcacion; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asistencia_marcacion (id, tipo, fecha_hora, latitud, longitud, distancia_metros, sucursal_id, usuario_id) FROM stdin;
1	ENTRADA	2026-11-07 08:30:00-04	-19.039699	-65.256900	0	1	8
2	SALIDA	2026-11-07 12:30:00-04	-19.039699	-65.256900	0	1	8
3	ENTRADA	2026-11-07 14:30:00-04	-19.039699	-65.256900	0	1	8
4	SALIDA	2026-11-07 19:30:00-04	-19.039699	-65.256900	0	1	8
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	group
3	auth	permission
4	contenttypes	contenttype
5	sessions	session
6	core	configuracion
7	core	registroactividad
8	core	sucursal
9	core	usuario
10	inventario	ajuste
11	inventario	articulo
12	inventario	categoria
13	inventario	detalleingreso
14	inventario	detalletraspaso
15	inventario	existencia
16	inventario	ingreso
17	inventario	movimiento
18	inventario	proveedor
19	inventario	traspaso
20	ventas	cliente
21	ventas	detalleventa
22	ventas	eventoorden
23	ventas	ordentrabajo
24	ventas	pago
25	ventas	receta
26	ventas	venta
27	caja	movimientocaja
28	caja	sesioncaja
29	asistencia	marcacion
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	3	add_permission
6	Can change permission	3	change_permission
7	Can delete permission	3	delete_permission
8	Can view permission	3	view_permission
9	Can add group	2	add_group
10	Can change group	2	change_group
11	Can delete group	2	delete_group
12	Can view group	2	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add usuario	9	add_usuario
22	Can change usuario	9	change_usuario
23	Can delete usuario	9	delete_usuario
24	Can view usuario	9	view_usuario
25	Can add sucursal	8	add_sucursal
26	Can change sucursal	8	change_sucursal
27	Can delete sucursal	8	delete_sucursal
28	Can view sucursal	8	view_sucursal
29	Can add registro de actividad	7	add_registroactividad
30	Can change registro de actividad	7	change_registroactividad
31	Can delete registro de actividad	7	delete_registroactividad
32	Can view registro de actividad	7	view_registroactividad
33	Can add parámetros del sistema	6	add_configuracion
34	Can change parámetros del sistema	6	change_configuracion
35	Can delete parámetros del sistema	6	delete_configuracion
36	Can view parámetros del sistema	6	view_configuracion
37	Can add categoría	12	add_categoria
38	Can change categoría	12	change_categoria
39	Can delete categoría	12	delete_categoria
40	Can view categoría	12	view_categoria
41	Can add proveedor	18	add_proveedor
42	Can change proveedor	18	change_proveedor
43	Can delete proveedor	18	delete_proveedor
44	Can view proveedor	18	view_proveedor
45	Puede ver, crear y editar proveedores	18	gestionar_proveedores
46	Can add artículo	11	add_articulo
47	Can change artículo	11	change_articulo
48	Can delete artículo	11	delete_articulo
49	Can view artículo	11	view_articulo
50	Puede consultar los artículos, sus precios y su stock	11	ver_articulos
51	Puede crear y editar artículos y categorías	11	gestionar_catalogo
52	Puede ver el kardex y los costos de los artículos	11	ver_kardex
53	Can add existencia	15	add_existencia
54	Can change existencia	15	change_existencia
55	Can delete existencia	15	delete_existencia
56	Can view existencia	15	view_existencia
57	Can add baja o ajuste	10	add_ajuste
58	Can change baja o ajuste	10	change_ajuste
59	Can delete baja o ajuste	10	delete_ajuste
60	Can view baja o ajuste	10	view_ajuste
61	Puede registrar bajas y ajustes de inventario	10	registrar_ajustes
62	Can add ingreso de mercadería	16	add_ingreso
63	Can change ingreso de mercadería	16	change_ingreso
64	Can delete ingreso de mercadería	16	delete_ingreso
65	Can view ingreso de mercadería	16	view_ingreso
66	Puede registrar ingresos de mercadería por compra	16	registrar_ingresos
67	Can add línea de ingreso	13	add_detalleingreso
68	Can change línea de ingreso	13	change_detalleingreso
69	Can delete línea de ingreso	13	delete_detalleingreso
70	Can view línea de ingreso	13	view_detalleingreso
71	Can add traspaso	19	add_traspaso
72	Can change traspaso	19	change_traspaso
73	Can delete traspaso	19	delete_traspaso
74	Can view traspaso	19	view_traspaso
75	Puede enviar mercadería a otra sucursal	19	enviar_traspasos
76	Puede recibir los traspasos dirigidos a su sucursal	19	recibir_traspasos
77	Can add movimiento de inventario	17	add_movimiento
78	Can change movimiento de inventario	17	change_movimiento
79	Can delete movimiento de inventario	17	delete_movimiento
80	Can view movimiento de inventario	17	view_movimiento
81	Can add línea de traspaso	14	add_detalletraspaso
82	Can change línea de traspaso	14	change_detalletraspaso
83	Can delete línea de traspaso	14	delete_detalletraspaso
84	Can view línea de traspaso	14	view_detalletraspaso
85	Can add venta	26	add_venta
86	Can change venta	26	change_venta
87	Can delete venta	26	delete_venta
88	Can view venta	26	view_venta
89	Puede registrar ventas y cobrar pagos	26	registrar_venta
90	Puede ver las ventas de todos los vendedores	26	ver_todas_ventas
91	Puede anular ventas	26	anular_venta
92	Can add pago	24	add_pago
93	Can change pago	24	change_pago
94	Can delete pago	24	delete_pago
95	Can view pago	24	view_pago
96	Can add detalle de venta	21	add_detalleventa
97	Can change detalle de venta	21	change_detalleventa
98	Can delete detalle de venta	21	delete_detalleventa
99	Can view detalle de venta	21	view_detalleventa
100	Can add cliente	20	add_cliente
101	Can change cliente	20	change_cliente
102	Can delete cliente	20	delete_cliente
103	Can view cliente	20	view_cliente
104	Puede registrar y editar clientes	20	gestionar_clientes
105	Can add orden de trabajo	23	add_ordentrabajo
106	Can change orden de trabajo	23	change_ordentrabajo
107	Can delete orden de trabajo	23	delete_ordentrabajo
108	Can view orden de trabajo	23	view_ordentrabajo
109	Puede consultar las órdenes de trabajo	23	ver_ordenes
110	Puede pasar las órdenes al taller y marcarlas como listas	23	actualizar_ordenes
111	Puede entregar los trabajos al cliente	23	entregar_ordenes
112	Puede autorizar la entrega de un trabajo con saldo pendiente	23	autorizar_entrega_con_saldo
113	Can add evento de la orden	22	add_eventoorden
114	Can change evento de la orden	22	change_eventoorden
115	Can delete evento de la orden	22	delete_eventoorden
116	Can view evento de la orden	22	view_eventoorden
117	Can add receta	25	add_receta
118	Can change receta	25	change_receta
119	Can delete receta	25	delete_receta
120	Can view receta	25	view_receta
121	Puede registrar recetas de los clientes	25	registrar_receta
122	Realiza exámenes visuales (figura como óptico responsable)	25	realizar_examen
123	Can add sesión de caja	28	add_sesioncaja
124	Can change sesión de caja	28	change_sesioncaja
125	Can delete sesión de caja	28	delete_sesioncaja
126	Can view sesión de caja	28	view_sesioncaja
127	Puede abrir su caja, registrar movimientos y cerrarla	28	operar_caja
128	Puede ver las cajas de todos los usuarios	28	ver_todas_cajas
129	Can add movimiento de caja	27	add_movimientocaja
130	Can change movimiento de caja	27	change_movimientocaja
131	Can delete movimiento de caja	27	delete_movimientocaja
132	Can view movimiento de caja	27	view_movimientocaja
133	Can add marcación	29	add_marcacion
134	Can change marcación	29	change_marcacion
135	Can delete marcación	29	delete_marcacion
136	Can view marcación	29	view_marcacion
137	Puede marcar su propia asistencia y ver su historial	29	marcar_asistencia
138	Puede ver las marcaciones de todo el personal	29	ver_todas_marcaciones
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
1	1	128
2	1	137
3	1	138
4	1	21
5	1	22
6	1	24
7	1	25
8	1	26
9	1	28
10	1	32
11	1	34
12	1	45
13	1	50
14	1	51
15	1	52
16	1	61
17	1	66
18	1	75
19	1	76
20	1	89
21	1	90
22	1	91
23	1	104
24	1	109
25	1	110
26	1	111
27	1	112
28	1	121
29	1	122
30	1	127
31	2	32
32	2	128
33	2	34
34	2	137
35	2	138
36	2	109
37	2	112
38	2	50
39	2	52
40	2	24
41	2	90
42	2	91
43	2	28
44	2	127
45	3	121
46	3	104
47	3	137
48	3	76
49	3	109
50	3	111
51	3	50
52	3	89
53	3	127
54	4	24
55	4	137
56	4	138
57	4	28
58	5	66
59	5	137
60	5	75
61	5	76
62	5	45
63	5	50
64	5	51
65	5	52
66	5	61
67	6	104
68	6	137
69	6	109
70	6	110
71	6	111
72	6	50
73	6	121
74	6	122
75	7	137
\.


--
-- Data for Name: caja_sesioncaja; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.caja_sesioncaja (id, estado, fecha_apertura, monto_inicial, fecha_cierre, monto_esperado, monto_contado, observacion, sucursal_id, usuario_id) FROM stdin;
1	CERRADA	2026-11-07 08:30:00-04	200.00	2026-11-07 19:30:00-04	550.00	550.00		1	3
\.


--
-- Data for Name: caja_movimientocaja; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.caja_movimientocaja (id, tipo, forma_pago, monto, concepto, fecha, usuario_id, sesion_id) FROM stdin;
1	INGRESO	EFECTIVO	350.00	Pago de la nota de venta 000001	2026-11-07 10:15:00-04	3	1
\.


--
-- Data for Name: core_configuracion; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.core_configuracion (id, anticipo_minimo_porcentaje) FROM stdin;
\.


--
-- Data for Name: core_usuario_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.core_usuario_groups (id, usuario_id, group_id) FROM stdin;
1	1	1
2	2	2
3	3	3
4	4	3
5	5	4
6	6	5
7	7	6
8	8	7
9	9	7
10	10	7
\.


--
-- Data for Name: core_usuario_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.core_usuario_user_permissions (id, usuario_id, permission_id) FROM stdin;
\.


--
-- Data for Name: inventario_categoria; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_categoria (id, nombre, descripcion, activa) FROM stdin;
1	Armazones	Monturas de metal, acetato y al aire	t
2	Lunas	Por tipo de material, diseño y tratamiento; la graduación va en la receta	t
3	Lentes de contacto		t
4	Accesorios	Estuches, paños, líquidos y cordones	t
5	Servicios	Examen visual y trabajos de taller; no controlan stock	t
\.


--
-- Data for Name: inventario_proveedor; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_proveedor (id, razon_social, nit, contacto, telefono, correo, direccion, activo) FROM stdin;
1	Distribuidora Óptica Andina SRL	1023456019	Carla Méndez	72800001			t
2	Lunas y Lentes Bolivia SA	2034567018	Marco Céspedes	72800002			t
\.


--
-- Data for Name: inventario_articulo; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_articulo (id, codigo, codigo_barras, nombre, marca, precio_venta, costo_promedio, stock_minimo, controla_stock, activo, categoria_id, proveedor_id, requiere_receta) FROM stdin;
8	SRV-001	\N	Examen visual computarizado		50.00	0.0000	0	f	t	5	\N	f
9	SRV-002	\N	Montaje de lunas en armazón propio		40.00	0.0000	0	f	t	5	\N	f
2	ARM-002	7790000000028	Armazón de acetato redondo	Urban	280.00	110.0000	2	t	t	1	1	f
6	ACC-001	7790000000042	Estuche rígido con paño		35.00	12.0000	10	t	t	4	1	f
7	ACC-002	7790000000059	Líquido limpiador 60 ml		25.00	9.0000	10	t	t	4	1	f
3	LUN-001	\N	Luna monofocal CR-39 antirreflejo		180.00	60.0000	6	t	t	2	2	t
4	LUN-002	\N	Luna progresiva policarbonato fotocromática		650.00	260.0000	4	t	t	2	2	t
5	LCO-001	7790000000035	Lentes de contacto mensuales (caja de 6)	AquaSoft	220.00	120.0000	3	t	t	3	2	f
1	ARM-001	7790000000011	Armazón metálico rectangular	Vision Pro	350.00	157.5000	2	t	t	1	1	f
\.


--
-- Data for Name: inventario_ajuste; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_ajuste (id, fecha, tipo, cantidad, motivo, articulo_id, sucursal_id, usuario_id) FROM stdin;
1	2026-11-08 13:52:28.089535-04	BAJA	1	Armazón con la bisagra rota al exhibirlo	2	1	6
\.


--
-- Data for Name: inventario_ingreso; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_ingreso (id, fecha, documento, observacion, proveedor_id, sucursal_id, usuario_id) FROM stdin;
1	2026-11-08 13:52:27.998247-04	F-0001520		1	1	6
2	2026-11-08 13:52:28.038816-04	F-0098211		2	1	6
3	2026-11-08 13:52:28.055234-04	F-0001587		1	1	6
\.


--
-- Data for Name: inventario_detalleingreso; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_detalleingreso (id, cantidad, costo_unitario, articulo_id, ingreso_id) FROM stdin;
1	10	150.0000	1	1
2	8	110.0000	2	1
3	30	12.0000	6	1
4	12	9.0000	7	1
5	40	60.0000	3	2
6	12	260.0000	4	2
7	15	120.0000	5	2
8	6	170.0000	1	3
\.


--
-- Data for Name: inventario_traspaso; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_traspaso (id, estado, observacion, fecha_envio, fecha_recepcion, destino_id, origen_id, usuario_envio_id, usuario_recepcion_id) FROM stdin;
1	RECIBIDO	Reposición semanal	2026-11-08 13:52:28.061323-04	2026-11-08 13:52:28.081367-04	2	1	6	4
2	ENVIADO	Pedido de la sucursal	2026-11-08 13:52:28.082547-04	\N	2	1	6	\N
\.


--
-- Data for Name: inventario_detalletraspaso; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_detalletraspaso (id, cantidad, articulo_id, traspaso_id) FROM stdin;
1	4	1	1
2	12	3	1
3	8	6	1
4	3	2	2
5	2	7	2
\.


--
-- Data for Name: inventario_existencia; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_existencia (id, cantidad, articulo_id, sucursal_id) FROM stdin;
6	12	4	1
7	15	5	1
3	22	6	1
8	4	1	2
9	12	3	2
10	8	6	2
4	10	7	1
2	4	2	1
1	11	1	1
5	26	3	1
\.


--
-- Data for Name: inventario_movimiento; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_movimiento (id, fecha, tipo, cantidad, costo_unitario, saldo, costo_promedio, referencia, ajuste_id, articulo_id, ingreso_id, sucursal_id, usuario_id, traspaso_id) FROM stdin;
1	2026-11-08 13:52:28.020415-04	COMPRA	10	150.0000	10	150.0000	Ingreso 000001	\N	1	1	1	6	\N
2	2026-11-08 13:52:28.026734-04	COMPRA	8	110.0000	8	110.0000	Ingreso 000001	\N	2	1	1	6	\N
3	2026-11-08 13:52:28.032524-04	COMPRA	30	12.0000	30	12.0000	Ingreso 000001	\N	6	1	1	6	\N
4	2026-11-08 13:52:28.037865-04	COMPRA	12	9.0000	12	9.0000	Ingreso 000001	\N	7	1	1	6	\N
5	2026-11-08 13:52:28.044557-04	COMPRA	40	60.0000	40	60.0000	Ingreso 000002	\N	3	2	1	6	\N
6	2026-11-08 13:52:28.049438-04	COMPRA	12	260.0000	12	260.0000	Ingreso 000002	\N	4	2	1	6	\N
7	2026-11-08 13:52:28.054264-04	COMPRA	15	120.0000	15	120.0000	Ingreso 000002	\N	5	2	1	6	\N
8	2026-11-08 13:52:28.060184-04	COMPRA	6	170.0000	16	157.5000	Ingreso 000003	\N	1	3	1	6	\N
9	2026-11-08 13:52:28.066228-04	TRASPASO_SALIDA	4	157.5000	12	157.5000	Traspaso 000001	\N	1	\N	1	6	1
10	2026-11-08 13:52:28.068361-04	TRASPASO_SALIDA	12	60.0000	28	60.0000	Traspaso 000001	\N	3	\N	1	6	1
11	2026-11-08 13:52:28.070405-04	TRASPASO_SALIDA	8	12.0000	22	12.0000	Traspaso 000001	\N	6	\N	1	6	1
12	2026-11-08 13:52:28.076095-04	TRASPASO_ENTRADA	4	157.5000	4	157.5000	Traspaso 000001	\N	1	\N	2	4	1
13	2026-11-08 13:52:28.078537-04	TRASPASO_ENTRADA	12	60.0000	12	60.0000	Traspaso 000001	\N	3	\N	2	4	1
14	2026-11-08 13:52:28.080934-04	TRASPASO_ENTRADA	8	12.0000	8	12.0000	Traspaso 000001	\N	6	\N	2	4	1
15	2026-11-08 13:52:28.085579-04	TRASPASO_SALIDA	3	110.0000	5	110.0000	Traspaso 000002	\N	2	\N	1	6	2
16	2026-11-08 13:52:28.087751-04	TRASPASO_SALIDA	2	9.0000	10	9.0000	Traspaso 000002	\N	7	\N	1	6	2
17	2026-11-08 13:52:28.095607-04	BAJA	1	110.0000	4	110.0000	Baja 000001	1	2	\N	1	6	\N
18	2026-11-08 13:52:28.132749-04	VENTA	1	157.5000	11	157.5000	Nota de venta 000001	\N	1	\N	1	3	\N
19	2026-11-08 13:52:28.135167-04	VENTA	2	60.0000	26	60.0000	Nota de venta 000001	\N	3	\N	1	3	\N
\.


--
-- Data for Name: ventas_cliente; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ventas_cliente (id, nombre, ci_nit, telefono, correo, fecha_nacimiento, direccion, fecha_registro) FROM stdin;
1	María Fernanda López Rojas	5555555	71234567		1990-04-12		2026-11-08 13:52:28.099529-04
2	Carlos Andrés Vargas Soliz	6666601	72345678		1968-09-03		2026-11-08 13:52:28.101868-04
3	Rosa Elena Quiroga Mendoza	7777702			\N		2026-11-08 13:52:28.103595-04
\.


--
-- Data for Name: ventas_venta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ventas_venta (id, fecha, cliente_nombre, cliente_ci, descripcion, total, estado, sucursal_id, vendedor_id, descuento, fecha_anulacion, motivo_anulacion, usuario_anulacion_id, cliente_id) FROM stdin;
1	2026-11-07 10:15:00-04	María Fernanda López Rojas	5555555		650.00	VIGENTE	1	3	60.00	\N		\N	1
\.


--
-- Data for Name: ventas_detalleventa; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ventas_detalleventa (id, cantidad, precio_unitario, costo_unitario, articulo_id, venta_id) FROM stdin;
1	1	350.00	157.5000	1	1
2	2	180.00	60.0000	3	1
\.


--
-- Data for Name: ventas_receta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ventas_receta (id, fecha, origen, medico, od_esfera, od_cilindro, od_eje, od_adicion, oi_esfera, oi_cilindro, oi_eje, oi_adicion, distancia_pupilar, observaciones, fecha_registro, cliente_id, optico_id, registrado_por_id) FROM stdin;
1	2025-10-24	EXAMEN		-1.00	-0.25	180	\N	-0.75	0.00	\N	\N	62.0		2026-11-08 13:52:28.116818-04	1	7	7
2	2026-11-06	EXAMEN		-1.25	-0.50	180	\N	-1.00	-0.25	170	\N	62.0	Uso permanente. Control en un año.	2026-11-08 13:52:28.11835-04	1	7	7
3	2026-10-29	EXTERNA	Dr. Mario Salinas · Clínica Oftalmológica Sucre	1.50	0.00	\N	2.00	1.75	0.00	\N	2.00	64.0	Presbicia. Sugiere lentes progresivos.	2026-11-08 13:52:28.119108-04	2	\N	3
\.


--
-- Data for Name: ventas_ordentrabajo; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ventas_ordentrabajo (id, estado, fecha, fecha_prometida, fecha_autorizacion, motivo_autorizacion, entrega_autorizada_por_id, venta_id, receta_id) FROM stdin;
1	LISTO	2026-11-07 10:15:00-04	2026-11-09	\N		\N	1	2
\.


--
-- Data for Name: ventas_eventoorden; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ventas_eventoorden (id, estado, fecha, nota, usuario_id, orden_id) FROM stdin;
1	PENDIENTE	2026-11-07 10:15:00-04	Generada con la Nota de venta 000001.	3	1
2	EN_TALLER	2026-11-07 11:00:00-04		7	1
3	LISTO	2026-11-07 17:40:00-04	Lunas talladas y montadas.	7	1
\.


--
-- Data for Name: ventas_pago; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ventas_pago (id, fecha, monto, forma_pago, movimiento_caja_id, usuario_id, venta_id) FROM stdin;
1	2026-11-07 10:15:00-04	350.00	EFECTIVO	1	3	1
\.


--
-- Name: asistencia_marcacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.asistencia_marcacion_id_seq', 4, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 7, true);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 75, true);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 138, true);


--
-- Name: caja_movimientocaja_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.caja_movimientocaja_id_seq', 1, true);


--
-- Name: caja_sesioncaja_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.caja_sesioncaja_id_seq', 1, true);


--
-- Name: core_configuracion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.core_configuracion_id_seq', 1, false);


--
-- Name: core_registroactividad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.core_registroactividad_id_seq', 1, false);


--
-- Name: core_sucursal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.core_sucursal_id_seq', 2, true);


--
-- Name: core_usuario_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.core_usuario_groups_id_seq', 10, true);


--
-- Name: core_usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.core_usuario_id_seq', 10, true);


--
-- Name: core_usuario_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.core_usuario_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 29, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 31, true);


--
-- Name: inventario_ajuste_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_ajuste_id_seq', 1, true);


--
-- Name: inventario_articulo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_articulo_id_seq', 9, true);


--
-- Name: inventario_categoria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_categoria_id_seq', 5, true);


--
-- Name: inventario_detalleingreso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_detalleingreso_id_seq', 8, true);


--
-- Name: inventario_detalletraspaso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_detalletraspaso_id_seq', 5, true);


--
-- Name: inventario_existencia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_existencia_id_seq', 10, true);


--
-- Name: inventario_ingreso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_ingreso_id_seq', 3, true);


--
-- Name: inventario_movimiento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_movimiento_id_seq', 19, true);


--
-- Name: inventario_proveedor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_proveedor_id_seq', 2, true);


--
-- Name: inventario_traspaso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_traspaso_id_seq', 2, true);


--
-- Name: ventas_cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ventas_cliente_id_seq', 3, true);


--
-- Name: ventas_detalleventa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ventas_detalleventa_id_seq', 2, true);


--
-- Name: ventas_eventoorden_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ventas_eventoorden_id_seq', 3, true);


--
-- Name: ventas_ordentrabajo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ventas_ordentrabajo_id_seq', 1, true);


--
-- Name: ventas_pago_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ventas_pago_id_seq', 1, true);


--
-- Name: ventas_receta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ventas_receta_id_seq', 3, true);


--
-- Name: ventas_venta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ventas_venta_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

\unrestrict DFHJqZcmGy2IX1FS49juH9HRnvrqZqH4NJspVqVdEYLpCAei0WhUUQIuqRMFbuN


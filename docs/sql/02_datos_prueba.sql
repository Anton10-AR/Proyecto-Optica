-- Ópticas Casimiro · Datos de prueba (seeds)
-- Generado con pg_dump a partir de `manage.py cargar_datos_prueba` sobre una base recién migrada.
-- Incluye roles y permisos, sucursales, usuarios, una caja y una venta de ejemplo, marcaciones,
-- el catálogo de inventario y sus movimientos iniciales (compras, traspasos y una baja).
-- Contraseña de todos los usuarios de prueba: Casimiro2026! (guardada con Argon2).
-- Ejecutar después de 01_esquema.sql sobre una base vacía.
-- La forma recomendada de recrear estos datos es: manage.py migrate && manage.py cargar_datos_prueba

--
-- PostgreSQL database dump
--

\restrict wJqvelhafkTXrAnb99TwfIAxBcN7su4YudnetBzVNLR4mkDOfHnvO6GIkzgVgXb

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
1	argon2$argon2id$v=19$m=102400,t=2,p=8$S3UyMktWeE9MdG9Weko2MFQ3Q0ZKcQ$sMZdeDyRC8HxmRGojWNKNVWw3astbwXcrmsPH9HrZbc	\N	f	administrador	Sofía	Torrico Lima	administrador@opticascasimiro.test	f	t	2026-11-08 12:03:10.135438-04	1000001	f	1	70000001	1
2	argon2$argon2id$v=19$m=102400,t=2,p=8$YUdtdnNDYjFqSU4xa2c3c3NOeXB1RA$KgND8JP1s/ROVizjOKysG94q4vbXsK6/1nTnG4AvxRk	\N	f	gerente	Daniel	Ortiz Paredes	gerente@opticascasimiro.test	f	t	2026-11-08 12:03:10.304804-04	1000002	f	2	70000002	1
3	argon2$argon2id$v=19$m=102400,t=2,p=8$WWlMSVVyVGZKZXFWelU0VFI0Vk1IVA$PcvN+RUknsxTLn5VDsvZaQRcbYwO4OLAwubPQOeLIng	\N	f	cajero1	Juan	Pérez Mamani	cajero1@opticascasimiro.test	f	t	2026-11-08 12:03:10.357678-04	1000003	f	3	70000003	1
4	argon2$argon2id$v=19$m=102400,t=2,p=8$aHlxczVyR2I0T2JUTkhUWjM1bDdKOQ$BAZMbV2ByB6k4iI+J6y0ZZleremhMyTxcQ6PO8aYO3c	\N	f	cajero2	Lucía	Quispe Vargas	cajero2@opticascasimiro.test	f	t	2026-11-08 12:03:10.408161-04	1000004	f	3	70000004	2
5	argon2$argon2id$v=19$m=102400,t=2,p=8$STdGckl6c2NrdXhCM2d3M29wcnhwMQ$vF6kv1kXqIJBJl79wx0D6dF3GDNTBEBQxNo+0EUsTMg	\N	f	rrhh	Valeria	Ramos Soliz	rrhh@opticascasimiro.test	f	t	2026-11-08 12:03:10.460835-04	1000005	f	4	70000005	1
6	argon2$argon2id$v=19$m=102400,t=2,p=8$MGRsSkpwUlNpZ2tDNldDZm5Pb3FwUw$fOwlOvANcN6yeANuxqtwiEqLEsSRcStoPQB1+IPX3OM	\N	f	almacen	Pedro	Rojas Torrez	almacen@opticascasimiro.test	f	t	2026-11-08 12:03:10.510733-04	1000006	f	5	70000006	1
7	argon2$argon2id$v=19$m=102400,t=2,p=8$N0pRQUdITTZjZm94YmJQNmtRM3ZMQQ$vbwdIcrSifqqGRIZoow4/bfvcjLxJYpilXiHppKVy7Y	\N	f	optico	Marta	Gutiérrez Choque	optico@opticascasimiro.test	f	t	2026-11-08 12:03:10.56414-04	1000007	f	6	70000007	1
8	argon2$argon2id$v=19$m=102400,t=2,p=8$RXprWGh5dE9pdlZlWDNtZ0tIMnV3Rw$IwBKtjtt+182Jy39tjzpzZxPFkKCNflieVKpf/ULveo	\N	f	empleado1	Luis	Fernández Cruz	empleado1@opticascasimiro.test	f	t	2026-11-08 12:03:10.612001-04	1000008	f	7	70000008	1
9	argon2$argon2id$v=19$m=102400,t=2,p=8$MzJ0NlVXc0FORzVaZk1SMzNESllXWg$UTNhoQ2eA+4pFNqzulQF4Jd3EjV0SGxOiILUrRYaJuI	\N	f	empleado2	Ana	Mendoza Arce	empleado2@opticascasimiro.test	f	t	2026-11-08 12:03:10.663736-04	1000009	f	7	70000009	2
10	argon2$argon2id$v=19$m=102400,t=2,p=8$UmhCWHozOGlYQW02dGdmYWQ5V3VmQQ$QLl35rJ5UV4VH0jhAAQHnyW98e6f5ivZvhKwlXsxlxQ	\N	f	exempleado	Jorge	Salazar Ríos	exempleado@opticascasimiro.test	f	f	2026-11-08 12:03:10.721257-04	1000010	f	7	70000010	1
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
6	core	registroactividad
7	core	sucursal
8	core	usuario
9	inventario	ajuste
10	inventario	articulo
11	inventario	categoria
12	inventario	detalleingreso
13	inventario	detalletraspaso
14	inventario	existencia
15	inventario	ingreso
16	inventario	movimiento
17	inventario	proveedor
18	inventario	traspaso
19	ventas	pago
20	ventas	venta
21	caja	movimientocaja
22	caja	sesioncaja
23	asistencia	marcacion
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
21	Can add usuario	8	add_usuario
22	Can change usuario	8	change_usuario
23	Can delete usuario	8	delete_usuario
24	Can view usuario	8	view_usuario
25	Can add sucursal	7	add_sucursal
26	Can change sucursal	7	change_sucursal
27	Can delete sucursal	7	delete_sucursal
28	Can view sucursal	7	view_sucursal
29	Can add registro de actividad	6	add_registroactividad
30	Can change registro de actividad	6	change_registroactividad
31	Can delete registro de actividad	6	delete_registroactividad
32	Can view registro de actividad	6	view_registroactividad
33	Can add categoría	11	add_categoria
34	Can change categoría	11	change_categoria
35	Can delete categoría	11	delete_categoria
36	Can view categoría	11	view_categoria
37	Can add proveedor	17	add_proveedor
38	Can change proveedor	17	change_proveedor
39	Can delete proveedor	17	delete_proveedor
40	Can view proveedor	17	view_proveedor
41	Puede ver, crear y editar proveedores	17	gestionar_proveedores
42	Can add artículo	10	add_articulo
43	Can change artículo	10	change_articulo
44	Can delete artículo	10	delete_articulo
45	Can view artículo	10	view_articulo
46	Puede consultar los artículos, sus precios y su stock	10	ver_articulos
47	Puede crear y editar artículos y categorías	10	gestionar_catalogo
48	Puede ver el kardex y los costos de los artículos	10	ver_kardex
49	Can add existencia	14	add_existencia
50	Can change existencia	14	change_existencia
51	Can delete existencia	14	delete_existencia
52	Can view existencia	14	view_existencia
53	Can add baja o ajuste	9	add_ajuste
54	Can change baja o ajuste	9	change_ajuste
55	Can delete baja o ajuste	9	delete_ajuste
56	Can view baja o ajuste	9	view_ajuste
57	Puede registrar bajas y ajustes de inventario	9	registrar_ajustes
58	Can add ingreso de mercadería	15	add_ingreso
59	Can change ingreso de mercadería	15	change_ingreso
60	Can delete ingreso de mercadería	15	delete_ingreso
61	Can view ingreso de mercadería	15	view_ingreso
62	Puede registrar ingresos de mercadería por compra	15	registrar_ingresos
63	Can add línea de ingreso	12	add_detalleingreso
64	Can change línea de ingreso	12	change_detalleingreso
65	Can delete línea de ingreso	12	delete_detalleingreso
66	Can view línea de ingreso	12	view_detalleingreso
67	Can add traspaso	18	add_traspaso
68	Can change traspaso	18	change_traspaso
69	Can delete traspaso	18	delete_traspaso
70	Can view traspaso	18	view_traspaso
71	Puede enviar mercadería a otra sucursal	18	enviar_traspasos
72	Puede recibir los traspasos dirigidos a su sucursal	18	recibir_traspasos
73	Can add movimiento de inventario	16	add_movimiento
74	Can change movimiento de inventario	16	change_movimiento
75	Can delete movimiento de inventario	16	delete_movimiento
76	Can view movimiento de inventario	16	view_movimiento
77	Can add línea de traspaso	13	add_detalletraspaso
78	Can change línea de traspaso	13	change_detalletraspaso
79	Can delete línea de traspaso	13	delete_detalletraspaso
80	Can view línea de traspaso	13	view_detalletraspaso
81	Can add venta	20	add_venta
82	Can change venta	20	change_venta
83	Can delete venta	20	delete_venta
84	Can view venta	20	view_venta
85	Puede registrar ventas y cobrar pagos	20	registrar_venta
86	Puede ver las ventas de todos los vendedores	20	ver_todas_ventas
87	Can add pago	19	add_pago
88	Can change pago	19	change_pago
89	Can delete pago	19	delete_pago
90	Can view pago	19	view_pago
91	Can add sesión de caja	22	add_sesioncaja
92	Can change sesión de caja	22	change_sesioncaja
93	Can delete sesión de caja	22	delete_sesioncaja
94	Can view sesión de caja	22	view_sesioncaja
95	Puede abrir su caja, registrar movimientos y cerrarla	22	operar_caja
96	Puede ver las cajas de todos los usuarios	22	ver_todas_cajas
97	Can add movimiento de caja	21	add_movimientocaja
98	Can change movimiento de caja	21	change_movimientocaja
99	Can delete movimiento de caja	21	delete_movimientocaja
100	Can view movimiento de caja	21	view_movimientocaja
101	Can add marcación	23	add_marcacion
102	Can change marcación	23	change_marcacion
103	Can delete marcación	23	delete_marcacion
104	Can view marcación	23	view_marcacion
105	Puede marcar su propia asistencia y ver su historial	23	marcar_asistencia
106	Puede ver las marcaciones de todo el personal	23	ver_todas_marcaciones
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
1	1	21
2	1	22
3	1	24
4	1	25
5	1	26
6	1	28
7	1	32
8	1	41
9	1	46
10	1	47
11	1	48
12	1	57
13	1	62
14	1	71
15	1	72
16	1	85
17	1	86
18	1	95
19	1	96
20	1	105
21	1	106
22	2	32
23	2	96
24	2	105
25	2	106
26	2	46
27	2	48
28	2	86
29	2	24
30	2	28
31	3	72
32	3	105
33	3	46
34	3	85
35	3	95
36	4	24
37	4	105
38	4	106
39	4	28
40	5	71
41	5	72
42	5	41
43	5	105
44	5	46
45	5	47
46	5	48
47	5	57
48	5	62
49	6	105
50	6	46
51	7	105
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

COPY public.inventario_articulo (id, codigo, codigo_barras, nombre, marca, precio_venta, costo_promedio, stock_minimo, controla_stock, activo, categoria_id, proveedor_id) FROM stdin;
8	SRV-001	\N	Examen visual computarizado		50.00	0.0000	0	f	t	5	\N
9	SRV-002	\N	Montaje de lunas en armazón propio		40.00	0.0000	0	f	t	5	\N
2	ARM-002	7790000000028	Armazón de acetato redondo	Urban	280.00	110.0000	2	t	t	1	1
6	ACC-001	7790000000042	Estuche rígido con paño		35.00	12.0000	10	t	t	4	1
7	ACC-002	7790000000059	Líquido limpiador 60 ml		25.00	9.0000	10	t	t	4	1
3	LUN-001	\N	Luna monofocal CR-39 antirreflejo		180.00	60.0000	6	t	t	2	2
4	LUN-002	\N	Luna progresiva policarbonato fotocromática		650.00	260.0000	4	t	t	2	2
5	LCO-001	7790000000035	Lentes de contacto mensuales (caja de 6)	AquaSoft	220.00	120.0000	3	t	t	3	2
1	ARM-001	7790000000011	Armazón metálico rectangular	Vision Pro	350.00	157.5000	2	t	t	1	1
\.


--
-- Data for Name: inventario_ajuste; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_ajuste (id, fecha, tipo, cantidad, motivo, articulo_id, sucursal_id, usuario_id) FROM stdin;
1	2026-11-08 12:03:10.908758-04	BAJA	1	Armazón con la bisagra rota al exhibirlo	2	1	6
\.


--
-- Data for Name: inventario_ingreso; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_ingreso (id, fecha, documento, observacion, proveedor_id, sucursal_id, usuario_id) FROM stdin;
1	2026-11-08 12:03:10.81891-04	F-0001520		1	1	6
2	2026-11-08 12:03:10.855589-04	F-0098211		2	1	6
3	2026-11-08 12:03:10.875375-04	F-0001587		1	1	6
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
1	RECIBIDO	Reposición semanal	2026-11-08 12:03:10.881121-04	2026-11-08 12:03:10.901037-04	2	1	6	4
2	ENVIADO	Pedido de la sucursal	2026-11-08 12:03:10.902112-04	\N	2	1	6	\N
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
1	12	1	1
5	28	3	1
3	22	6	1
8	4	1	2
9	12	3	2
10	8	6	2
4	10	7	1
2	4	2	1
\.


--
-- Data for Name: inventario_movimiento; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_movimiento (id, fecha, tipo, cantidad, costo_unitario, saldo, costo_promedio, referencia, ajuste_id, articulo_id, ingreso_id, sucursal_id, usuario_id, traspaso_id) FROM stdin;
1	2026-11-08 12:03:10.838976-04	COMPRA	10	150.0000	10	150.0000	Ingreso 000001	\N	1	1	1	6	\N
2	2026-11-08 12:03:10.845074-04	COMPRA	8	110.0000	8	110.0000	Ingreso 000001	\N	2	1	1	6	\N
3	2026-11-08 12:03:10.849952-04	COMPRA	30	12.0000	30	12.0000	Ingreso 000001	\N	6	1	1	6	\N
4	2026-11-08 12:03:10.854708-04	COMPRA	12	9.0000	12	9.0000	Ingreso 000001	\N	7	1	1	6	\N
5	2026-11-08 12:03:10.861121-04	COMPRA	40	60.0000	40	60.0000	Ingreso 000002	\N	3	2	1	6	\N
6	2026-11-08 12:03:10.867575-04	COMPRA	12	260.0000	12	260.0000	Ingreso 000002	\N	4	2	1	6	\N
7	2026-11-08 12:03:10.874486-04	COMPRA	15	120.0000	15	120.0000	Ingreso 000002	\N	5	2	1	6	\N
8	2026-11-08 12:03:10.880188-04	COMPRA	6	170.0000	16	157.5000	Ingreso 000003	\N	1	3	1	6	\N
9	2026-11-08 12:03:10.885276-04	TRASPASO_SALIDA	4	157.5000	12	157.5000	Traspaso 000001	\N	1	\N	1	6	1
10	2026-11-08 12:03:10.887284-04	TRASPASO_SALIDA	12	60.0000	28	60.0000	Traspaso 000001	\N	3	\N	1	6	1
11	2026-11-08 12:03:10.889409-04	TRASPASO_SALIDA	8	12.0000	22	12.0000	Traspaso 000001	\N	6	\N	1	6	1
12	2026-11-08 12:03:10.896147-04	TRASPASO_ENTRADA	4	157.5000	4	157.5000	Traspaso 000001	\N	1	\N	2	4	1
13	2026-11-08 12:03:10.898409-04	TRASPASO_ENTRADA	12	60.0000	12	60.0000	Traspaso 000001	\N	3	\N	2	4	1
14	2026-11-08 12:03:10.900655-04	TRASPASO_ENTRADA	8	12.0000	8	12.0000	Traspaso 000001	\N	6	\N	2	4	1
15	2026-11-08 12:03:10.904825-04	TRASPASO_SALIDA	3	110.0000	5	110.0000	Traspaso 000002	\N	2	\N	1	6	2
16	2026-11-08 12:03:10.907105-04	TRASPASO_SALIDA	2	9.0000	10	9.0000	Traspaso 000002	\N	7	\N	1	6	2
17	2026-11-08 12:03:10.913924-04	BAJA	1	110.0000	4	110.0000	Baja 000001	1	2	\N	1	6	\N
\.


--
-- Data for Name: ventas_venta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ventas_venta (id, fecha, cliente_nombre, cliente_ci, descripcion, total, estado, sucursal_id, vendedor_id) FROM stdin;
1	2026-11-07 10:15:00-04	Cliente de prueba	5555555	Armazón y lunas monofocales	650.00	VIGENTE	1	3
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

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 51, true);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 106, true);


--
-- Name: caja_movimientocaja_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.caja_movimientocaja_id_seq', 1, true);


--
-- Name: caja_sesioncaja_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.caja_sesioncaja_id_seq', 1, true);


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

SELECT pg_catalog.setval('public.django_content_type_id_seq', 23, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 27, true);


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

SELECT pg_catalog.setval('public.inventario_movimiento_id_seq', 17, true);


--
-- Name: inventario_proveedor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_proveedor_id_seq', 2, true);


--
-- Name: inventario_traspaso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_traspaso_id_seq', 2, true);


--
-- Name: ventas_pago_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ventas_pago_id_seq', 1, true);


--
-- Name: ventas_venta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ventas_venta_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

\unrestrict wJqvelhafkTXrAnb99TwfIAxBcN7su4YudnetBzVNLR4mkDOfHnvO6GIkzgVgXb


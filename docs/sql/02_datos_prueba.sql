-- Ópticas Casimiro · Datos de prueba (seeds)
-- Generado con pg_dump a partir de `manage.py cargar_datos_prueba` sobre una base recién migrada.
-- Incluye roles y permisos, sucursales, usuarios, una caja y una venta de ejemplo con sus líneas, marcaciones,
-- el catálogo de inventario y sus movimientos iniciales (compras, traspasos y una baja),
-- clientes con su historial de recetas y una orden de trabajo lista con saldo pendiente,
-- y horarios, feriados, permisos y dos semanas de marcaciones del personal.
-- Contraseña de todos los usuarios de prueba: Casimiro2026! (guardada con Argon2).
-- Ejecutar después de 01_esquema.sql sobre una base vacía.
-- La forma recomendada de recrear estos datos es: manage.py migrate && manage.py cargar_datos_prueba

--
-- PostgreSQL database dump
--

\restrict mv5tBDPrsOHh0AOhZClJNrwDZCC3SGACR9iXQfyzFrH2XKKnyGQ2Th9PMcLFSbz

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
-- Data for Name: asistencia_horario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asistencia_horario (id, nombre, descripcion, activo) FROM stdin;
1	Horario partido	Lunes a viernes con descanso al mediodía; sábado en la mañana.	t
2	Medio tiempo (mañana)	Lunes a sábado en la mañana.	t
\.


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

COPY public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id, cargo) FROM stdin;
1	argon2$argon2id$v=19$m=102400,t=2,p=8$d0Zac0JhazhrU0lsYm81ZzhLVFpoZg$K4u2kndfJxZ8cQv7YlGLVv8MJFNMbDAL8/wntOf9YPI	\N	f	administrador	Sofía	Torrico Lima	administrador@opticascasimiro.test	f	t	2026-11-08 14:38:42.743225-04	1000001	f	1	70000001	1	Administradora
2	argon2$argon2id$v=19$m=102400,t=2,p=8$M1JmWXNQaGtNdmJvVjVnNlk0RXNXeQ$cgNzd3lMHx4YO5y2zKnFPnFdA5px3TUe60VaJ+D7nSo	\N	f	gerente	Daniel	Ortiz Paredes	gerente@opticascasimiro.test	f	t	2026-11-08 14:38:42.910515-04	1000002	f	2	70000002	1	Gerente general
3	argon2$argon2id$v=19$m=102400,t=2,p=8$enBFZlFyUjdXRHJ2Wld5NmxJNzdodA$S0B1/cM1LtJUizgeQb+gVDYu0oNLrA3ZJNPaxRh8qWU	\N	f	cajero1	Juan	Pérez Mamani	cajero1@opticascasimiro.test	f	t	2026-11-08 14:38:42.960602-04	1000003	f	3	70000003	1	Vendedor
4	argon2$argon2id$v=19$m=102400,t=2,p=8$Z0pPekJWaUIxTFQ5Zk5yb1VnQjJ2aA$ZzVx+rYRQZi/msD/G/ZBU52mb4kOs6sPX2oEbMx3D0g	\N	f	cajero2	Lucía	Quispe Vargas	cajero2@opticascasimiro.test	f	t	2026-11-08 14:38:43.008233-04	1000004	f	3	70000004	2	Vendedora
5	argon2$argon2id$v=19$m=102400,t=2,p=8$VXRBdmRkYk1wOHpYMGNYUmFPUWYyNw$ukReftMoLZTVwr0kKoeobdbxYsUsa1mSaP+mWjQzHuc	\N	f	rrhh	Valeria	Ramos Soliz	rrhh@opticascasimiro.test	f	t	2026-11-08 14:38:43.062292-04	1000005	f	4	70000005	1	Encargada de personal
6	argon2$argon2id$v=19$m=102400,t=2,p=8$WVo0clVSbU5Td0VTbWhjSlZ2MVNzNw$cno/ZNtCbWmL6nQnUZsmUX53RMQuWqKPzCVvBDDDakg	\N	f	almacen	Pedro	Rojas Torrez	almacen@opticascasimiro.test	f	t	2026-11-08 14:38:43.113927-04	1000006	f	5	70000006	1	Encargado de almacén
7	argon2$argon2id$v=19$m=102400,t=2,p=8$M0F6b0tPWFhSbnFFUFNTclJtZFlaTw$KIF9RFOGAh8FNTlJ9qrlkMAhkB2FX+l/pLZRXM0N/Rc	\N	f	optico	Marta	Gutiérrez Choque	optico@opticascasimiro.test	f	t	2026-11-08 14:38:43.169218-04	1000007	f	6	70000007	1	Optometrista
8	argon2$argon2id$v=19$m=102400,t=2,p=8$Mkl6VUJXcFV2cGJ0dmZMeXF4VVZubw$GmjNM4t9A+R0HBslypo4Dsq58y/kDu6I8IohgZtzUDA	\N	f	empleado1	Luis	Fernández Cruz	empleado1@opticascasimiro.test	f	t	2026-11-08 14:38:43.219055-04	1000008	f	7	70000008	1	Auxiliar de taller
9	argon2$argon2id$v=19$m=102400,t=2,p=8$N3FUd1hBRnUzOTdMemxNbnRwaFI2WA$dFkk30dwaLB+qfSEQV6AHi5vp/pp62zZ8KHjDXA49bo	\N	f	empleado2	Ana	Mendoza Arce	empleado2@opticascasimiro.test	f	t	2026-11-08 14:38:43.271542-04	1000009	f	7	70000009	2	Auxiliar de limpieza
10	argon2$argon2id$v=19$m=102400,t=2,p=8$WGk1ZW1DVEVQM1J6OHpCWmMyS0Y2RQ$1WEawFJncGedyavvGJZdbeklbvDdgdfRfVVAhKpvHy0	\N	f	exempleado	Jorge	Salazar Ríos	exempleado@opticascasimiro.test	f	f	2026-11-08 14:38:43.322426-04	1000010	f	7	70000010	1	Auxiliar de taller
\.


--
-- Data for Name: asistencia_asignacionhorario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asistencia_asignacionhorario (id, desde, fecha_registro, registrado_por_id, usuario_id, horario_id) FROM stdin;
1	2026-10-09	2026-11-08 14:38:43.597095-04	5	1	1
2	2026-10-09	2026-11-08 14:38:43.60156-04	5	2	1
3	2026-10-09	2026-11-08 14:38:43.602152-04	5	3	1
4	2026-10-09	2026-11-08 14:38:43.602624-04	5	4	1
5	2026-10-09	2026-11-08 14:38:43.603064-04	5	5	1
6	2026-10-09	2026-11-08 14:38:43.603492-04	5	6	1
7	2026-10-09	2026-11-08 14:38:43.60389-04	5	7	1
8	2026-10-09	2026-11-08 14:38:43.604283-04	5	8	1
9	2026-10-09	2026-11-08 14:38:43.604765-04	5	9	2
\.


--
-- Data for Name: asistencia_ausencia; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asistencia_ausencia (id, tipo, desde, hasta, motivo, fecha_registro, registrado_por_id, usuario_id) FROM stdin;
1	VACACION	2026-10-27	2026-10-29	Vacación anual	2026-11-08 14:38:43.605752-04	5	9
2	PERMISO	2026-10-30	2026-10-30	Trámite personal	2026-11-08 14:38:43.608568-04	5	3
\.


--
-- Data for Name: asistencia_feriado; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asistencia_feriado (id, fecha, nombre) FROM stdin;
1	2026-01-01	Año Nuevo
2	2026-01-22	Día del Estado Plurinacional
3	2026-02-16	Carnaval
4	2026-02-17	Carnaval
5	2026-04-03	Viernes Santo
6	2026-05-01	Día del Trabajo
7	2026-05-25	Aniversario de Chuquisaca
8	2026-06-04	Corpus Christi
9	2026-06-21	Año Nuevo Andino Amazónico
10	2026-08-06	Día de la Independencia
11	2026-11-02	Todos Santos
12	2026-12-25	Navidad
\.


--
-- Data for Name: asistencia_marcacion; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asistencia_marcacion (id, tipo, fecha_hora, latitud, longitud, distancia_metros, sucursal_id, usuario_id) FROM stdin;
1	ENTRADA	2026-11-07 08:30:00-04	-19.039699	-65.256900	0	1	8
2	SALIDA	2026-11-07 12:30:00-04	-19.039699	-65.256900	0	1	8
3	ENTRADA	2026-11-07 14:30:00-04	-19.039699	-65.256900	0	1	8
4	SALIDA	2026-11-07 19:30:00-04	-19.039699	-65.256900	0	1	8
5	ENTRADA	2026-11-07 08:57:00-04	-19.039699	-65.256900	0	1	1
6	SALIDA	2026-11-07 13:02:00-04	-19.039699	-65.256900	0	1	1
7	ENTRADA	2026-11-06 08:28:00-04	-19.039699	-65.256900	0	1	1
8	SALIDA	2026-11-06 12:33:00-04	-19.039699	-65.256900	0	1	1
9	ENTRADA	2026-11-06 14:29:00-04	-19.039699	-65.256900	0	1	1
10	SALIDA	2026-11-06 19:34:00-04	-19.039699	-65.256900	0	1	1
11	ENTRADA	2026-11-05 08:29:00-04	-19.039699	-65.256900	0	1	1
12	SALIDA	2026-11-05 12:34:00-04	-19.039699	-65.256900	0	1	1
13	ENTRADA	2026-11-05 14:26:00-04	-19.039699	-65.256900	0	1	1
14	SALIDA	2026-11-05 19:35:00-04	-19.039699	-65.256900	0	1	1
15	ENTRADA	2026-11-04 08:26:00-04	-19.039699	-65.256900	0	1	1
16	SALIDA	2026-11-04 12:35:00-04	-19.039699	-65.256900	0	1	1
17	ENTRADA	2026-11-04 14:27:00-04	-19.039699	-65.256900	0	1	1
18	SALIDA	2026-11-04 19:31:00-04	-19.039699	-65.256900	0	1	1
19	ENTRADA	2026-11-03 08:27:00-04	-19.039699	-65.256900	0	1	1
20	SALIDA	2026-11-03 12:31:00-04	-19.039699	-65.256900	0	1	1
21	ENTRADA	2026-11-03 14:28:00-04	-19.039699	-65.256900	0	1	1
22	SALIDA	2026-11-03 19:32:00-04	-19.039699	-65.256900	0	1	1
23	ENTRADA	2026-10-31 08:56:00-04	-19.039699	-65.256900	0	1	1
24	SALIDA	2026-10-31 13:04:00-04	-19.039699	-65.256900	0	1	1
25	ENTRADA	2026-10-30 08:27:00-04	-19.039699	-65.256900	0	1	1
26	SALIDA	2026-10-30 12:35:00-04	-19.039699	-65.256900	0	1	1
27	ENTRADA	2026-10-30 14:28:00-04	-19.039699	-65.256900	0	1	1
28	SALIDA	2026-10-30 19:31:00-04	-19.039699	-65.256900	0	1	1
29	ENTRADA	2026-10-29 08:28:00-04	-19.039699	-65.256900	0	1	1
30	SALIDA	2026-10-29 12:31:00-04	-19.039699	-65.256900	0	1	1
31	ENTRADA	2026-10-29 14:29:00-04	-19.039699	-65.256900	0	1	1
32	SALIDA	2026-10-29 19:32:00-04	-19.039699	-65.256900	0	1	1
33	ENTRADA	2026-10-28 08:29:00-04	-19.039699	-65.256900	0	1	1
34	SALIDA	2026-10-28 12:32:00-04	-19.039699	-65.256900	0	1	1
35	ENTRADA	2026-10-28 14:26:00-04	-19.039699	-65.256900	0	1	1
36	SALIDA	2026-10-28 19:33:00-04	-19.039699	-65.256900	0	1	1
37	ENTRADA	2026-10-27 08:26:00-04	-19.039699	-65.256900	0	1	1
38	SALIDA	2026-10-27 12:33:00-04	-19.039699	-65.256900	0	1	1
39	ENTRADA	2026-10-27 14:27:00-04	-19.039699	-65.256900	0	1	1
40	SALIDA	2026-10-27 19:34:00-04	-19.039699	-65.256900	0	1	1
41	ENTRADA	2026-10-26 08:27:00-04	-19.039699	-65.256900	0	1	1
42	SALIDA	2026-10-26 12:34:00-04	-19.039699	-65.256900	0	1	1
43	ENTRADA	2026-10-26 14:28:00-04	-19.039699	-65.256900	0	1	1
44	SALIDA	2026-10-26 19:35:00-04	-19.039699	-65.256900	0	1	1
45	ENTRADA	2026-11-07 08:57:00-04	-19.039699	-65.256900	0	1	2
46	SALIDA	2026-11-07 13:02:00-04	-19.039699	-65.256900	0	1	2
47	ENTRADA	2026-11-06 08:28:00-04	-19.039699	-65.256900	0	1	2
48	SALIDA	2026-11-06 12:33:00-04	-19.039699	-65.256900	0	1	2
49	ENTRADA	2026-11-06 14:29:00-04	-19.039699	-65.256900	0	1	2
50	SALIDA	2026-11-06 19:34:00-04	-19.039699	-65.256900	0	1	2
51	ENTRADA	2026-11-05 08:29:00-04	-19.039699	-65.256900	0	1	2
52	SALIDA	2026-11-05 12:34:00-04	-19.039699	-65.256900	0	1	2
53	ENTRADA	2026-11-05 14:26:00-04	-19.039699	-65.256900	0	1	2
54	SALIDA	2026-11-05 19:35:00-04	-19.039699	-65.256900	0	1	2
55	ENTRADA	2026-11-04 08:26:00-04	-19.039699	-65.256900	0	1	2
56	SALIDA	2026-11-04 12:35:00-04	-19.039699	-65.256900	0	1	2
57	ENTRADA	2026-11-04 14:27:00-04	-19.039699	-65.256900	0	1	2
58	SALIDA	2026-11-04 19:31:00-04	-19.039699	-65.256900	0	1	2
59	ENTRADA	2026-11-03 08:27:00-04	-19.039699	-65.256900	0	1	2
60	SALIDA	2026-11-03 12:31:00-04	-19.039699	-65.256900	0	1	2
61	ENTRADA	2026-11-03 14:28:00-04	-19.039699	-65.256900	0	1	2
62	SALIDA	2026-11-03 19:32:00-04	-19.039699	-65.256900	0	1	2
63	ENTRADA	2026-10-31 08:56:00-04	-19.039699	-65.256900	0	1	2
64	SALIDA	2026-10-31 13:04:00-04	-19.039699	-65.256900	0	1	2
65	ENTRADA	2026-10-30 08:27:00-04	-19.039699	-65.256900	0	1	2
66	SALIDA	2026-10-30 12:35:00-04	-19.039699	-65.256900	0	1	2
67	ENTRADA	2026-10-30 14:28:00-04	-19.039699	-65.256900	0	1	2
68	SALIDA	2026-10-30 19:31:00-04	-19.039699	-65.256900	0	1	2
69	ENTRADA	2026-10-29 08:28:00-04	-19.039699	-65.256900	0	1	2
70	SALIDA	2026-10-29 12:31:00-04	-19.039699	-65.256900	0	1	2
71	ENTRADA	2026-10-29 14:29:00-04	-19.039699	-65.256900	0	1	2
72	SALIDA	2026-10-29 19:32:00-04	-19.039699	-65.256900	0	1	2
73	ENTRADA	2026-10-28 08:29:00-04	-19.039699	-65.256900	0	1	2
74	SALIDA	2026-10-28 12:32:00-04	-19.039699	-65.256900	0	1	2
75	ENTRADA	2026-10-28 14:26:00-04	-19.039699	-65.256900	0	1	2
76	SALIDA	2026-10-28 19:33:00-04	-19.039699	-65.256900	0	1	2
77	ENTRADA	2026-10-27 08:26:00-04	-19.039699	-65.256900	0	1	2
78	SALIDA	2026-10-27 12:33:00-04	-19.039699	-65.256900	0	1	2
79	ENTRADA	2026-10-27 14:27:00-04	-19.039699	-65.256900	0	1	2
80	SALIDA	2026-10-27 19:34:00-04	-19.039699	-65.256900	0	1	2
81	ENTRADA	2026-10-26 08:27:00-04	-19.039699	-65.256900	0	1	2
82	SALIDA	2026-10-26 12:34:00-04	-19.039699	-65.256900	0	1	2
83	ENTRADA	2026-10-26 14:28:00-04	-19.039699	-65.256900	0	1	2
84	SALIDA	2026-10-26 19:35:00-04	-19.039699	-65.256900	0	1	2
85	ENTRADA	2026-11-07 08:57:00-04	-19.039699	-65.256900	0	1	3
86	SALIDA	2026-11-07 13:02:00-04	-19.039699	-65.256900	0	1	3
87	ENTRADA	2026-11-06 08:28:00-04	-19.039699	-65.256900	0	1	3
88	SALIDA	2026-11-06 12:33:00-04	-19.039699	-65.256900	0	1	3
89	ENTRADA	2026-11-06 14:29:00-04	-19.039699	-65.256900	0	1	3
90	SALIDA	2026-11-06 19:34:00-04	-19.039699	-65.256900	0	1	3
91	ENTRADA	2026-11-05 08:41:00-04	-19.039699	-65.256900	0	1	3
92	SALIDA	2026-11-05 12:34:00-04	-19.039699	-65.256900	0	1	3
93	ENTRADA	2026-11-05 14:26:00-04	-19.039699	-65.256900	0	1	3
94	SALIDA	2026-11-05 19:35:00-04	-19.039699	-65.256900	0	1	3
95	ENTRADA	2026-11-04 08:26:00-04	-19.039699	-65.256900	0	1	3
96	SALIDA	2026-11-04 12:35:00-04	-19.039699	-65.256900	0	1	3
97	ENTRADA	2026-11-04 14:27:00-04	-19.039699	-65.256900	0	1	3
98	SALIDA	2026-11-04 19:31:00-04	-19.039699	-65.256900	0	1	3
99	ENTRADA	2026-11-03 08:27:00-04	-19.039699	-65.256900	0	1	3
100	SALIDA	2026-11-03 12:31:00-04	-19.039699	-65.256900	0	1	3
101	ENTRADA	2026-11-03 14:28:00-04	-19.039699	-65.256900	0	1	3
102	SALIDA	2026-11-03 19:32:00-04	-19.039699	-65.256900	0	1	3
103	ENTRADA	2026-10-31 08:56:00-04	-19.039699	-65.256900	0	1	3
104	SALIDA	2026-10-31 13:04:00-04	-19.039699	-65.256900	0	1	3
105	ENTRADA	2026-10-29 08:28:00-04	-19.039699	-65.256900	0	1	3
106	SALIDA	2026-10-29 12:31:00-04	-19.039699	-65.256900	0	1	3
107	ENTRADA	2026-10-29 14:29:00-04	-19.039699	-65.256900	0	1	3
108	SALIDA	2026-10-29 19:32:00-04	-19.039699	-65.256900	0	1	3
109	ENTRADA	2026-10-28 08:34:00-04	-19.039699	-65.256900	0	1	3
110	SALIDA	2026-10-28 12:32:00-04	-19.039699	-65.256900	0	1	3
111	ENTRADA	2026-10-28 14:26:00-04	-19.039699	-65.256900	0	1	3
112	SALIDA	2026-10-28 19:33:00-04	-19.039699	-65.256900	0	1	3
113	ENTRADA	2026-10-27 08:26:00-04	-19.039699	-65.256900	0	1	3
114	SALIDA	2026-10-27 12:33:00-04	-19.039699	-65.256900	0	1	3
115	ENTRADA	2026-10-27 14:27:00-04	-19.039699	-65.256900	0	1	3
116	SALIDA	2026-10-27 19:34:00-04	-19.039699	-65.256900	0	1	3
117	ENTRADA	2026-10-26 08:27:00-04	-19.039699	-65.256900	0	1	3
118	SALIDA	2026-10-26 12:34:00-04	-19.039699	-65.256900	0	1	3
119	ENTRADA	2026-10-26 14:28:00-04	-19.039699	-65.256900	0	1	3
120	SALIDA	2026-10-26 19:35:00-04	-19.039699	-65.256900	0	1	3
121	ENTRADA	2026-11-07 08:57:00-04	-19.039699	-65.256900	0	2	4
122	SALIDA	2026-11-07 13:02:00-04	-19.039699	-65.256900	0	2	4
123	ENTRADA	2026-11-06 08:28:00-04	-19.039699	-65.256900	0	2	4
124	SALIDA	2026-11-06 12:33:00-04	-19.039699	-65.256900	0	2	4
125	ENTRADA	2026-11-06 14:29:00-04	-19.039699	-65.256900	0	2	4
126	SALIDA	2026-11-06 19:34:00-04	-19.039699	-65.256900	0	2	4
127	ENTRADA	2026-11-05 08:29:00-04	-19.039699	-65.256900	0	2	4
128	SALIDA	2026-11-05 12:34:00-04	-19.039699	-65.256900	0	2	4
129	ENTRADA	2026-11-05 14:26:00-04	-19.039699	-65.256900	0	2	4
130	SALIDA	2026-11-05 19:35:00-04	-19.039699	-65.256900	0	2	4
131	ENTRADA	2026-11-04 08:26:00-04	-19.039699	-65.256900	0	2	4
132	SALIDA	2026-11-04 12:35:00-04	-19.039699	-65.256900	0	2	4
133	ENTRADA	2026-11-04 14:27:00-04	-19.039699	-65.256900	0	2	4
134	SALIDA	2026-11-04 19:31:00-04	-19.039699	-65.256900	0	2	4
135	ENTRADA	2026-11-03 08:27:00-04	-19.039699	-65.256900	0	2	4
136	SALIDA	2026-11-03 12:31:00-04	-19.039699	-65.256900	0	2	4
137	ENTRADA	2026-11-03 14:28:00-04	-19.039699	-65.256900	0	2	4
138	SALIDA	2026-11-03 19:32:00-04	-19.039699	-65.256900	0	2	4
139	ENTRADA	2026-10-31 08:56:00-04	-19.039699	-65.256900	0	2	4
140	SALIDA	2026-10-31 13:04:00-04	-19.039699	-65.256900	0	2	4
141	ENTRADA	2026-10-30 08:27:00-04	-19.039699	-65.256900	0	2	4
142	SALIDA	2026-10-30 12:35:00-04	-19.039699	-65.256900	0	2	4
143	ENTRADA	2026-10-30 14:28:00-04	-19.039699	-65.256900	0	2	4
144	SALIDA	2026-10-30 19:31:00-04	-19.039699	-65.256900	0	2	4
145	ENTRADA	2026-10-29 08:28:00-04	-19.039699	-65.256900	0	2	4
146	SALIDA	2026-10-29 12:31:00-04	-19.039699	-65.256900	0	2	4
147	ENTRADA	2026-10-29 14:29:00-04	-19.039699	-65.256900	0	2	4
148	SALIDA	2026-10-29 19:32:00-04	-19.039699	-65.256900	0	2	4
149	ENTRADA	2026-10-28 08:29:00-04	-19.039699	-65.256900	0	2	4
150	SALIDA	2026-10-28 12:32:00-04	-19.039699	-65.256900	0	2	4
151	ENTRADA	2026-10-28 14:26:00-04	-19.039699	-65.256900	0	2	4
152	SALIDA	2026-10-28 19:33:00-04	-19.039699	-65.256900	0	2	4
153	ENTRADA	2026-10-27 08:26:00-04	-19.039699	-65.256900	0	2	4
154	SALIDA	2026-10-27 12:33:00-04	-19.039699	-65.256900	0	2	4
155	ENTRADA	2026-10-27 14:27:00-04	-19.039699	-65.256900	0	2	4
156	SALIDA	2026-10-27 19:34:00-04	-19.039699	-65.256900	0	2	4
157	ENTRADA	2026-10-26 08:27:00-04	-19.039699	-65.256900	0	2	4
158	SALIDA	2026-10-26 12:34:00-04	-19.039699	-65.256900	0	2	4
159	ENTRADA	2026-10-26 14:28:00-04	-19.039699	-65.256900	0	2	4
160	SALIDA	2026-10-26 19:35:00-04	-19.039699	-65.256900	0	2	4
161	ENTRADA	2026-11-07 08:57:00-04	-19.039699	-65.256900	0	1	5
162	SALIDA	2026-11-07 13:02:00-04	-19.039699	-65.256900	0	1	5
163	ENTRADA	2026-11-06 08:28:00-04	-19.039699	-65.256900	0	1	5
164	SALIDA	2026-11-06 12:33:00-04	-19.039699	-65.256900	0	1	5
165	ENTRADA	2026-11-06 14:29:00-04	-19.039699	-65.256900	0	1	5
166	SALIDA	2026-11-06 19:34:00-04	-19.039699	-65.256900	0	1	5
167	ENTRADA	2026-11-05 08:29:00-04	-19.039699	-65.256900	0	1	5
168	SALIDA	2026-11-05 12:34:00-04	-19.039699	-65.256900	0	1	5
169	ENTRADA	2026-11-05 14:26:00-04	-19.039699	-65.256900	0	1	5
170	SALIDA	2026-11-05 19:35:00-04	-19.039699	-65.256900	0	1	5
171	ENTRADA	2026-11-04 08:26:00-04	-19.039699	-65.256900	0	1	5
172	SALIDA	2026-11-04 12:35:00-04	-19.039699	-65.256900	0	1	5
173	ENTRADA	2026-11-04 14:27:00-04	-19.039699	-65.256900	0	1	5
174	SALIDA	2026-11-04 19:31:00-04	-19.039699	-65.256900	0	1	5
175	ENTRADA	2026-11-03 08:27:00-04	-19.039699	-65.256900	0	1	5
176	SALIDA	2026-11-03 12:31:00-04	-19.039699	-65.256900	0	1	5
177	ENTRADA	2026-11-03 14:28:00-04	-19.039699	-65.256900	0	1	5
178	SALIDA	2026-11-03 19:32:00-04	-19.039699	-65.256900	0	1	5
179	ENTRADA	2026-10-31 08:56:00-04	-19.039699	-65.256900	0	1	5
180	SALIDA	2026-10-31 13:04:00-04	-19.039699	-65.256900	0	1	5
181	ENTRADA	2026-10-30 08:27:00-04	-19.039699	-65.256900	0	1	5
182	SALIDA	2026-10-30 12:35:00-04	-19.039699	-65.256900	0	1	5
183	ENTRADA	2026-10-30 14:28:00-04	-19.039699	-65.256900	0	1	5
184	SALIDA	2026-10-30 19:31:00-04	-19.039699	-65.256900	0	1	5
185	ENTRADA	2026-10-29 08:28:00-04	-19.039699	-65.256900	0	1	5
186	SALIDA	2026-10-29 12:31:00-04	-19.039699	-65.256900	0	1	5
187	ENTRADA	2026-10-29 14:29:00-04	-19.039699	-65.256900	0	1	5
188	SALIDA	2026-10-29 19:32:00-04	-19.039699	-65.256900	0	1	5
189	ENTRADA	2026-10-28 08:29:00-04	-19.039699	-65.256900	0	1	5
190	SALIDA	2026-10-28 12:32:00-04	-19.039699	-65.256900	0	1	5
191	ENTRADA	2026-10-28 14:26:00-04	-19.039699	-65.256900	0	1	5
192	SALIDA	2026-10-28 19:33:00-04	-19.039699	-65.256900	0	1	5
193	ENTRADA	2026-10-27 08:26:00-04	-19.039699	-65.256900	0	1	5
194	SALIDA	2026-10-27 12:33:00-04	-19.039699	-65.256900	0	1	5
195	ENTRADA	2026-10-27 14:27:00-04	-19.039699	-65.256900	0	1	5
196	SALIDA	2026-10-27 19:34:00-04	-19.039699	-65.256900	0	1	5
197	ENTRADA	2026-10-26 08:27:00-04	-19.039699	-65.256900	0	1	5
198	SALIDA	2026-10-26 12:34:00-04	-19.039699	-65.256900	0	1	5
199	ENTRADA	2026-10-26 14:28:00-04	-19.039699	-65.256900	0	1	5
200	SALIDA	2026-10-26 19:35:00-04	-19.039699	-65.256900	0	1	5
201	ENTRADA	2026-11-07 08:57:00-04	-19.039699	-65.256900	0	1	6
202	SALIDA	2026-11-07 13:02:00-04	-19.039699	-65.256900	0	1	6
203	ENTRADA	2026-11-06 08:28:00-04	-19.039699	-65.256900	0	1	6
204	SALIDA	2026-11-06 12:33:00-04	-19.039699	-65.256900	0	1	6
205	ENTRADA	2026-11-06 14:29:00-04	-19.039699	-65.256900	0	1	6
206	SALIDA	2026-11-06 19:34:00-04	-19.039699	-65.256900	0	1	6
207	ENTRADA	2026-11-05 08:29:00-04	-19.039699	-65.256900	0	1	6
208	SALIDA	2026-11-05 12:34:00-04	-19.039699	-65.256900	0	1	6
209	ENTRADA	2026-11-05 14:26:00-04	-19.039699	-65.256900	0	1	6
210	SALIDA	2026-11-05 19:35:00-04	-19.039699	-65.256900	0	1	6
211	ENTRADA	2026-11-04 08:26:00-04	-19.039699	-65.256900	0	1	6
212	SALIDA	2026-11-04 12:35:00-04	-19.039699	-65.256900	0	1	6
213	ENTRADA	2026-11-04 14:27:00-04	-19.039699	-65.256900	0	1	6
214	SALIDA	2026-11-04 19:31:00-04	-19.039699	-65.256900	0	1	6
215	ENTRADA	2026-11-03 08:27:00-04	-19.039699	-65.256900	0	1	6
216	SALIDA	2026-11-03 12:31:00-04	-19.039699	-65.256900	0	1	6
217	ENTRADA	2026-11-03 14:28:00-04	-19.039699	-65.256900	0	1	6
218	SALIDA	2026-11-03 19:32:00-04	-19.039699	-65.256900	0	1	6
219	ENTRADA	2026-10-31 08:56:00-04	-19.039699	-65.256900	0	1	6
220	SALIDA	2026-10-31 13:04:00-04	-19.039699	-65.256900	0	1	6
221	ENTRADA	2026-10-30 08:27:00-04	-19.039699	-65.256900	0	1	6
222	SALIDA	2026-10-30 12:35:00-04	-19.039699	-65.256900	0	1	6
223	ENTRADA	2026-10-30 14:28:00-04	-19.039699	-65.256900	0	1	6
224	SALIDA	2026-10-30 19:31:00-04	-19.039699	-65.256900	0	1	6
225	ENTRADA	2026-10-29 08:28:00-04	-19.039699	-65.256900	0	1	6
226	SALIDA	2026-10-29 12:31:00-04	-19.039699	-65.256900	0	1	6
227	ENTRADA	2026-10-29 14:29:00-04	-19.039699	-65.256900	0	1	6
228	SALIDA	2026-10-29 19:32:00-04	-19.039699	-65.256900	0	1	6
229	ENTRADA	2026-10-28 08:29:00-04	-19.039699	-65.256900	0	1	6
230	SALIDA	2026-10-28 12:32:00-04	-19.039699	-65.256900	0	1	6
231	ENTRADA	2026-10-28 14:26:00-04	-19.039699	-65.256900	0	1	6
232	SALIDA	2026-10-28 19:33:00-04	-19.039699	-65.256900	0	1	6
233	ENTRADA	2026-10-27 08:26:00-04	-19.039699	-65.256900	0	1	6
234	SALIDA	2026-10-27 12:33:00-04	-19.039699	-65.256900	0	1	6
235	ENTRADA	2026-10-27 14:27:00-04	-19.039699	-65.256900	0	1	6
236	SALIDA	2026-10-27 19:34:00-04	-19.039699	-65.256900	0	1	6
237	ENTRADA	2026-10-26 08:27:00-04	-19.039699	-65.256900	0	1	6
238	SALIDA	2026-10-26 12:34:00-04	-19.039699	-65.256900	0	1	6
239	ENTRADA	2026-10-26 14:28:00-04	-19.039699	-65.256900	0	1	6
240	SALIDA	2026-10-26 19:35:00-04	-19.039699	-65.256900	0	1	6
241	ENTRADA	2026-11-07 08:57:00-04	-19.039699	-65.256900	0	1	7
242	SALIDA	2026-11-07 13:02:00-04	-19.039699	-65.256900	0	1	7
243	ENTRADA	2026-11-06 08:28:00-04	-19.039699	-65.256900	0	1	7
244	SALIDA	2026-11-06 12:33:00-04	-19.039699	-65.256900	0	1	7
245	ENTRADA	2026-11-06 14:29:00-04	-19.039699	-65.256900	0	1	7
246	SALIDA	2026-11-06 19:34:00-04	-19.039699	-65.256900	0	1	7
247	ENTRADA	2026-11-05 08:29:00-04	-19.039699	-65.256900	0	1	7
248	SALIDA	2026-11-05 12:34:00-04	-19.039699	-65.256900	0	1	7
249	ENTRADA	2026-11-05 14:26:00-04	-19.039699	-65.256900	0	1	7
250	SALIDA	2026-11-05 19:35:00-04	-19.039699	-65.256900	0	1	7
251	ENTRADA	2026-11-04 08:26:00-04	-19.039699	-65.256900	0	1	7
252	SALIDA	2026-11-04 12:35:00-04	-19.039699	-65.256900	0	1	7
253	ENTRADA	2026-11-04 14:27:00-04	-19.039699	-65.256900	0	1	7
254	SALIDA	2026-11-04 19:31:00-04	-19.039699	-65.256900	0	1	7
255	ENTRADA	2026-11-03 08:27:00-04	-19.039699	-65.256900	0	1	7
256	SALIDA	2026-11-03 12:31:00-04	-19.039699	-65.256900	0	1	7
257	ENTRADA	2026-11-03 14:28:00-04	-19.039699	-65.256900	0	1	7
258	SALIDA	2026-11-03 19:32:00-04	-19.039699	-65.256900	0	1	7
259	ENTRADA	2026-10-31 08:56:00-04	-19.039699	-65.256900	0	1	7
260	SALIDA	2026-10-31 13:04:00-04	-19.039699	-65.256900	0	1	7
261	ENTRADA	2026-10-30 08:27:00-04	-19.039699	-65.256900	0	1	7
262	SALIDA	2026-10-30 12:35:00-04	-19.039699	-65.256900	0	1	7
263	ENTRADA	2026-10-30 14:28:00-04	-19.039699	-65.256900	0	1	7
264	SALIDA	2026-10-30 19:31:00-04	-19.039699	-65.256900	0	1	7
265	ENTRADA	2026-10-29 08:28:00-04	-19.039699	-65.256900	0	1	7
266	SALIDA	2026-10-29 12:31:00-04	-19.039699	-65.256900	0	1	7
267	ENTRADA	2026-10-29 14:29:00-04	-19.039699	-65.256900	0	1	7
268	SALIDA	2026-10-29 19:32:00-04	-19.039699	-65.256900	0	1	7
269	ENTRADA	2026-10-28 08:29:00-04	-19.039699	-65.256900	0	1	7
270	SALIDA	2026-10-28 12:32:00-04	-19.039699	-65.256900	0	1	7
271	ENTRADA	2026-10-28 14:26:00-04	-19.039699	-65.256900	0	1	7
272	SALIDA	2026-10-28 19:33:00-04	-19.039699	-65.256900	0	1	7
273	ENTRADA	2026-10-27 08:26:00-04	-19.039699	-65.256900	0	1	7
274	SALIDA	2026-10-27 12:33:00-04	-19.039699	-65.256900	0	1	7
275	ENTRADA	2026-10-27 14:27:00-04	-19.039699	-65.256900	0	1	7
276	SALIDA	2026-10-27 19:34:00-04	-19.039699	-65.256900	0	1	7
277	ENTRADA	2026-10-26 08:27:00-04	-19.039699	-65.256900	0	1	7
278	SALIDA	2026-10-26 12:34:00-04	-19.039699	-65.256900	0	1	7
279	ENTRADA	2026-10-26 14:28:00-04	-19.039699	-65.256900	0	1	7
280	SALIDA	2026-10-26 19:35:00-04	-19.039699	-65.256900	0	1	7
281	ENTRADA	2026-11-06 08:52:00-04	-19.039699	-65.256900	0	1	8
282	SALIDA	2026-11-06 12:33:00-04	-19.039699	-65.256900	0	1	8
283	ENTRADA	2026-11-06 14:29:00-04	-19.039699	-65.256900	0	1	8
284	SALIDA	2026-11-06 19:34:00-04	-19.039699	-65.256900	0	1	8
285	ENTRADA	2026-11-05 08:29:00-04	-19.039699	-65.256900	0	1	8
286	SALIDA	2026-11-05 12:34:00-04	-19.039699	-65.256900	0	1	8
287	ENTRADA	2026-11-05 14:26:00-04	-19.039699	-65.256900	0	1	8
288	SALIDA	2026-11-05 19:35:00-04	-19.039699	-65.256900	0	1	8
289	ENTRADA	2026-11-04 08:26:00-04	-19.039699	-65.256900	0	1	8
290	SALIDA	2026-11-04 12:35:00-04	-19.039699	-65.256900	0	1	8
291	ENTRADA	2026-11-03 08:27:00-04	-19.039699	-65.256900	0	1	8
292	SALIDA	2026-11-03 12:31:00-04	-19.039699	-65.256900	0	1	8
293	ENTRADA	2026-11-03 14:28:00-04	-19.039699	-65.256900	0	1	8
294	SALIDA	2026-11-03 19:32:00-04	-19.039699	-65.256900	0	1	8
295	ENTRADA	2026-10-31 08:56:00-04	-19.039699	-65.256900	0	1	8
296	SALIDA	2026-10-31 13:04:00-04	-19.039699	-65.256900	0	1	8
297	ENTRADA	2026-10-30 08:27:00-04	-19.039699	-65.256900	0	1	8
298	SALIDA	2026-10-30 12:35:00-04	-19.039699	-65.256900	0	1	8
299	ENTRADA	2026-10-30 14:28:00-04	-19.039699	-65.256900	0	1	8
300	SALIDA	2026-10-30 19:31:00-04	-19.039699	-65.256900	0	1	8
301	ENTRADA	2026-10-28 08:29:00-04	-19.039699	-65.256900	0	1	8
302	SALIDA	2026-10-28 12:32:00-04	-19.039699	-65.256900	0	1	8
303	ENTRADA	2026-10-28 14:26:00-04	-19.039699	-65.256900	0	1	8
304	SALIDA	2026-10-28 19:33:00-04	-19.039699	-65.256900	0	1	8
305	ENTRADA	2026-10-27 08:26:00-04	-19.039699	-65.256900	0	1	8
306	SALIDA	2026-10-27 12:33:00-04	-19.039699	-65.256900	0	1	8
307	ENTRADA	2026-10-27 14:27:00-04	-19.039699	-65.256900	0	1	8
308	SALIDA	2026-10-27 19:34:00-04	-19.039699	-65.256900	0	1	8
309	ENTRADA	2026-10-26 08:27:00-04	-19.039699	-65.256900	0	1	8
310	SALIDA	2026-10-26 12:34:00-04	-19.039699	-65.256900	0	1	8
311	ENTRADA	2026-10-26 14:28:00-04	-19.039699	-65.256900	0	1	8
312	SALIDA	2026-10-26 19:35:00-04	-19.039699	-65.256900	0	1	8
313	ENTRADA	2026-11-07 08:27:00-04	-19.039699	-65.256900	0	2	9
314	SALIDA	2026-11-07 12:32:00-04	-19.039699	-65.256900	0	2	9
315	ENTRADA	2026-11-06 08:28:00-04	-19.039699	-65.256900	0	2	9
316	SALIDA	2026-11-06 12:33:00-04	-19.039699	-65.256900	0	2	9
317	ENTRADA	2026-11-05 08:29:00-04	-19.039699	-65.256900	0	2	9
318	SALIDA	2026-11-05 12:34:00-04	-19.039699	-65.256900	0	2	9
319	ENTRADA	2026-11-04 08:26:00-04	-19.039699	-65.256900	0	2	9
320	SALIDA	2026-11-04 12:35:00-04	-19.039699	-65.256900	0	2	9
321	ENTRADA	2026-11-03 08:27:00-04	-19.039699	-65.256900	0	2	9
322	SALIDA	2026-11-03 12:31:00-04	-19.039699	-65.256900	0	2	9
323	ENTRADA	2026-10-31 08:26:00-04	-19.039699	-65.256900	0	2	9
324	SALIDA	2026-10-31 12:34:00-04	-19.039699	-65.256900	0	2	9
325	ENTRADA	2026-10-30 08:27:00-04	-19.039699	-65.256900	0	2	9
326	SALIDA	2026-10-30 12:35:00-04	-19.039699	-65.256900	0	2	9
327	ENTRADA	2026-10-26 08:27:00-04	-19.039699	-65.256900	0	2	9
328	SALIDA	2026-10-26 12:34:00-04	-19.039699	-65.256900	0	2	9
\.


--
-- Data for Name: asistencia_tramohorario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.asistencia_tramohorario (id, dia_semana, hora_entrada, hora_salida, horario_id) FROM stdin;
1	0	08:30:00	12:30:00	1
2	0	14:30:00	19:30:00	1
3	1	08:30:00	12:30:00	1
4	1	14:30:00	19:30:00	1
5	2	08:30:00	12:30:00	1
6	2	14:30:00	19:30:00	1
7	3	08:30:00	12:30:00	1
8	3	14:30:00	19:30:00	1
9	4	08:30:00	12:30:00	1
10	4	14:30:00	19:30:00	1
11	5	09:00:00	13:00:00	1
12	0	08:30:00	12:30:00	2
13	1	08:30:00	12:30:00	2
14	2	08:30:00	12:30:00	2
15	3	08:30:00	12:30:00	2
16	4	08:30:00	12:30:00	2
17	5	08:30:00	12:30:00	2
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
29	asistencia	asignacionhorario
30	asistencia	ausencia
31	asistencia	feriado
32	asistencia	horario
33	asistencia	marcacion
34	asistencia	tramohorario
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
37	Puede definir la tolerancia de atraso	6	configurar_asistencia
38	Can add categoría	12	add_categoria
39	Can change categoría	12	change_categoria
40	Can delete categoría	12	delete_categoria
41	Can view categoría	12	view_categoria
42	Can add proveedor	18	add_proveedor
43	Can change proveedor	18	change_proveedor
44	Can delete proveedor	18	delete_proveedor
45	Can view proveedor	18	view_proveedor
46	Puede ver, crear y editar proveedores	18	gestionar_proveedores
47	Can add artículo	11	add_articulo
48	Can change artículo	11	change_articulo
49	Can delete artículo	11	delete_articulo
50	Can view artículo	11	view_articulo
51	Puede consultar los artículos, sus precios y su stock	11	ver_articulos
52	Puede crear y editar artículos y categorías	11	gestionar_catalogo
53	Puede ver el kardex y los costos de los artículos	11	ver_kardex
54	Can add existencia	15	add_existencia
55	Can change existencia	15	change_existencia
56	Can delete existencia	15	delete_existencia
57	Can view existencia	15	view_existencia
58	Can add baja o ajuste	10	add_ajuste
59	Can change baja o ajuste	10	change_ajuste
60	Can delete baja o ajuste	10	delete_ajuste
61	Can view baja o ajuste	10	view_ajuste
62	Puede registrar bajas y ajustes de inventario	10	registrar_ajustes
63	Can add ingreso de mercadería	16	add_ingreso
64	Can change ingreso de mercadería	16	change_ingreso
65	Can delete ingreso de mercadería	16	delete_ingreso
66	Can view ingreso de mercadería	16	view_ingreso
67	Puede registrar ingresos de mercadería por compra	16	registrar_ingresos
68	Can add línea de ingreso	13	add_detalleingreso
69	Can change línea de ingreso	13	change_detalleingreso
70	Can delete línea de ingreso	13	delete_detalleingreso
71	Can view línea de ingreso	13	view_detalleingreso
72	Can add traspaso	19	add_traspaso
73	Can change traspaso	19	change_traspaso
74	Can delete traspaso	19	delete_traspaso
75	Can view traspaso	19	view_traspaso
76	Puede enviar mercadería a otra sucursal	19	enviar_traspasos
77	Puede recibir los traspasos dirigidos a su sucursal	19	recibir_traspasos
78	Can add movimiento de inventario	17	add_movimiento
79	Can change movimiento de inventario	17	change_movimiento
80	Can delete movimiento de inventario	17	delete_movimiento
81	Can view movimiento de inventario	17	view_movimiento
82	Can add línea de traspaso	14	add_detalletraspaso
83	Can change línea de traspaso	14	change_detalletraspaso
84	Can delete línea de traspaso	14	delete_detalletraspaso
85	Can view línea de traspaso	14	view_detalletraspaso
86	Can add venta	26	add_venta
87	Can change venta	26	change_venta
88	Can delete venta	26	delete_venta
89	Can view venta	26	view_venta
90	Puede registrar ventas y cobrar pagos	26	registrar_venta
91	Puede ver las ventas de todos los vendedores	26	ver_todas_ventas
92	Puede anular ventas	26	anular_venta
93	Can add pago	24	add_pago
94	Can change pago	24	change_pago
95	Can delete pago	24	delete_pago
96	Can view pago	24	view_pago
97	Can add detalle de venta	21	add_detalleventa
98	Can change detalle de venta	21	change_detalleventa
99	Can delete detalle de venta	21	delete_detalleventa
100	Can view detalle de venta	21	view_detalleventa
101	Can add cliente	20	add_cliente
102	Can change cliente	20	change_cliente
103	Can delete cliente	20	delete_cliente
104	Can view cliente	20	view_cliente
105	Puede registrar y editar clientes	20	gestionar_clientes
106	Can add orden de trabajo	23	add_ordentrabajo
107	Can change orden de trabajo	23	change_ordentrabajo
108	Can delete orden de trabajo	23	delete_ordentrabajo
109	Can view orden de trabajo	23	view_ordentrabajo
110	Puede consultar las órdenes de trabajo	23	ver_ordenes
111	Puede pasar las órdenes al taller y marcarlas como listas	23	actualizar_ordenes
112	Puede entregar los trabajos al cliente	23	entregar_ordenes
113	Puede autorizar la entrega de un trabajo con saldo pendiente	23	autorizar_entrega_con_saldo
114	Can add evento de la orden	22	add_eventoorden
115	Can change evento de la orden	22	change_eventoorden
116	Can delete evento de la orden	22	delete_eventoorden
117	Can view evento de la orden	22	view_eventoorden
118	Can add receta	25	add_receta
119	Can change receta	25	change_receta
120	Can delete receta	25	delete_receta
121	Can view receta	25	view_receta
122	Puede registrar recetas de los clientes	25	registrar_receta
123	Realiza exámenes visuales (figura como óptico responsable)	25	realizar_examen
124	Can add sesión de caja	28	add_sesioncaja
125	Can change sesión de caja	28	change_sesioncaja
126	Can delete sesión de caja	28	delete_sesioncaja
127	Can view sesión de caja	28	view_sesioncaja
128	Puede abrir su caja, registrar movimientos y cerrarla	28	operar_caja
129	Puede ver las cajas de todos los usuarios	28	ver_todas_cajas
130	Can add movimiento de caja	27	add_movimientocaja
131	Can change movimiento de caja	27	change_movimientocaja
132	Can delete movimiento de caja	27	delete_movimientocaja
133	Can view movimiento de caja	27	view_movimientocaja
134	Can add marcación	33	add_marcacion
135	Can change marcación	33	change_marcacion
136	Can delete marcación	33	delete_marcacion
137	Can view marcación	33	view_marcacion
138	Puede marcar su propia asistencia y ver su historial	33	marcar_asistencia
139	Puede ver la asistencia y los reportes de todo el personal	33	ver_todas_marcaciones
140	Can add feriado	31	add_feriado
141	Can change feriado	31	change_feriado
142	Can delete feriado	31	delete_feriado
143	Can view feriado	31	view_feriado
144	Puede gestionar el calendario de feriados	31	gestionar_feriados
145	Can add horario	32	add_horario
146	Can change horario	32	change_horario
147	Can delete horario	32	delete_horario
148	Can view horario	32	view_horario
149	Puede gestionar los horarios, asignarlos y editar el cargo del personal	32	gestionar_horarios
150	Can add permiso o vacación	30	add_ausencia
151	Can change permiso o vacación	30	change_ausencia
152	Can delete permiso o vacación	30	delete_ausencia
153	Can view permiso o vacación	30	view_ausencia
154	Puede registrar permisos y vacaciones del personal	30	gestionar_ausencias
155	Can add asignación de horario	29	add_asignacionhorario
156	Can change asignación de horario	29	change_asignacionhorario
157	Can delete asignación de horario	29	delete_asignacionhorario
158	Can view asignación de horario	29	view_asignacionhorario
159	Can add tramo del horario	34	add_tramohorario
160	Can change tramo del horario	34	change_tramohorario
161	Can delete tramo del horario	34	delete_tramohorario
162	Can view tramo del horario	34	view_tramohorario
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
1	1	128
2	1	129
3	1	138
4	1	139
5	1	144
6	1	21
7	1	22
8	1	149
9	1	24
10	1	25
11	1	26
12	1	154
13	1	28
14	1	32
15	1	34
16	1	37
17	1	46
18	1	51
19	1	52
20	1	53
21	1	62
22	1	67
23	1	76
24	1	77
25	1	90
26	1	91
27	1	92
28	1	105
29	1	110
30	1	111
31	1	112
32	1	113
33	1	122
34	1	123
35	2	32
36	2	128
37	2	129
38	2	34
39	2	37
40	2	138
41	2	139
42	2	110
43	2	92
44	2	113
45	2	51
46	2	53
47	2	24
48	2	91
49	2	28
50	3	128
51	3	122
52	3	105
53	3	138
54	3	77
55	3	110
56	3	112
57	3	51
58	3	90
59	4	37
60	4	138
61	4	139
62	4	144
63	4	149
64	4	24
65	4	154
66	4	28
67	5	67
68	5	138
69	5	76
70	5	77
71	5	46
72	5	51
73	5	52
74	5	53
75	5	62
76	6	105
77	6	138
78	6	110
79	6	111
80	6	112
81	6	51
82	6	122
83	6	123
84	7	138
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

COPY public.core_configuracion (id, anticipo_minimo_porcentaje, tolerancia_minutos) FROM stdin;
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
1	2026-11-08 14:38:43.498435-04	BAJA	1	Armazón con la bisagra rota al exhibirlo	2	1	6
\.


--
-- Data for Name: inventario_ingreso; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario_ingreso (id, fecha, documento, observacion, proveedor_id, sucursal_id, usuario_id) FROM stdin;
1	2026-11-08 14:38:43.413652-04	F-0001520		1	1	6
2	2026-11-08 14:38:43.449088-04	F-0098211		2	1	6
3	2026-11-08 14:38:43.464881-04	F-0001587		1	1	6
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
1	RECIBIDO	Reposición semanal	2026-11-08 14:38:43.471122-04	2026-11-08 14:38:43.490082-04	2	1	6	4
2	ENVIADO	Pedido de la sucursal	2026-11-08 14:38:43.491099-04	\N	2	1	6	\N
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
1	2026-11-08 14:38:43.433472-04	COMPRA	10	150.0000	10	150.0000	Ingreso 000001	\N	1	1	1	6	\N
2	2026-11-08 14:38:43.439216-04	COMPRA	8	110.0000	8	110.0000	Ingreso 000001	\N	2	1	1	6	\N
3	2026-11-08 14:38:43.443807-04	COMPRA	30	12.0000	30	12.0000	Ingreso 000001	\N	6	1	1	6	\N
4	2026-11-08 14:38:43.448277-04	COMPRA	12	9.0000	12	9.0000	Ingreso 000001	\N	7	1	1	6	\N
5	2026-11-08 14:38:43.454327-04	COMPRA	40	60.0000	40	60.0000	Ingreso 000002	\N	3	2	1	6	\N
6	2026-11-08 14:38:43.459452-04	COMPRA	12	260.0000	12	260.0000	Ingreso 000002	\N	4	2	1	6	\N
7	2026-11-08 14:38:43.464069-04	COMPRA	15	120.0000	15	120.0000	Ingreso 000002	\N	5	2	1	6	\N
8	2026-11-08 14:38:43.470193-04	COMPRA	6	170.0000	16	157.5000	Ingreso 000003	\N	1	3	1	6	\N
9	2026-11-08 14:38:43.475155-04	TRASPASO_SALIDA	4	157.5000	12	157.5000	Traspaso 000001	\N	1	\N	1	6	1
10	2026-11-08 14:38:43.477138-04	TRASPASO_SALIDA	12	60.0000	28	60.0000	Traspaso 000001	\N	3	\N	1	6	1
11	2026-11-08 14:38:43.479123-04	TRASPASO_SALIDA	8	12.0000	22	12.0000	Traspaso 000001	\N	6	\N	1	6	1
12	2026-11-08 14:38:43.485126-04	TRASPASO_ENTRADA	4	157.5000	4	157.5000	Traspaso 000001	\N	1	\N	2	4	1
13	2026-11-08 14:38:43.487469-04	TRASPASO_ENTRADA	12	60.0000	12	60.0000	Traspaso 000001	\N	3	\N	2	4	1
14	2026-11-08 14:38:43.489662-04	TRASPASO_ENTRADA	8	12.0000	8	12.0000	Traspaso 000001	\N	6	\N	2	4	1
15	2026-11-08 14:38:43.493795-04	TRASPASO_SALIDA	3	110.0000	5	110.0000	Traspaso 000002	\N	2	\N	1	6	2
16	2026-11-08 14:38:43.496149-04	TRASPASO_SALIDA	2	9.0000	10	9.0000	Traspaso 000002	\N	7	\N	1	6	2
17	2026-11-08 14:38:43.504206-04	BAJA	1	110.0000	4	110.0000	Baja 000001	1	2	\N	1	6	\N
18	2026-11-08 14:38:43.538069-04	VENTA	1	157.5000	11	157.5000	Nota de venta 000001	\N	1	\N	1	3	\N
19	2026-11-08 14:38:43.539659-04	VENTA	2	60.0000	26	60.0000	Nota de venta 000001	\N	3	\N	1	3	\N
\.


--
-- Data for Name: ventas_cliente; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ventas_cliente (id, nombre, ci_nit, telefono, correo, fecha_nacimiento, direccion, fecha_registro) FROM stdin;
1	María Fernanda López Rojas	5555555	71234567		1990-04-12		2026-11-08 14:38:43.507386-04
2	Carlos Andrés Vargas Soliz	6666601	72345678		1968-09-03		2026-11-08 14:38:43.509421-04
3	Rosa Elena Quiroga Mendoza	7777702			\N		2026-11-08 14:38:43.511024-04
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
1	2025-10-24	EXAMEN		-1.00	-0.25	180	\N	-0.75	0.00	\N	\N	62.0		2026-11-08 14:38:43.523193-04	1	7	7
2	2026-11-06	EXAMEN		-1.25	-0.50	180	\N	-1.00	-0.25	170	\N	62.0	Uso permanente. Control en un año.	2026-11-08 14:38:43.524713-04	1	7	7
3	2026-10-29	EXTERNA	Dr. Mario Salinas · Clínica Oftalmológica Sucre	1.50	0.00	\N	2.00	1.75	0.00	\N	2.00	64.0	Presbicia. Sugiere lentes progresivos.	2026-11-08 14:38:43.525329-04	2	\N	3
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
-- Name: asistencia_asignacionhorario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.asistencia_asignacionhorario_id_seq', 9, true);


--
-- Name: asistencia_ausencia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.asistencia_ausencia_id_seq', 2, true);


--
-- Name: asistencia_feriado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.asistencia_feriado_id_seq', 12, true);


--
-- Name: asistencia_horario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.asistencia_horario_id_seq', 2, true);


--
-- Name: asistencia_marcacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.asistencia_marcacion_id_seq', 328, true);


--
-- Name: asistencia_tramohorario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.asistencia_tramohorario_id_seq', 17, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 7, true);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 84, true);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 162, true);


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

SELECT pg_catalog.setval('public.django_content_type_id_seq', 34, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 33, true);


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

\unrestrict mv5tBDPrsOHh0AOhZClJNrwDZCC3SGACR9iXQfyzFrH2XKKnyGQ2Th9PMcLFSbz


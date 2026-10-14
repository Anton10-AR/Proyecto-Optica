-- Ópticas Casimiro · Datos de prueba (seeds) del módulo de Gestión de Usuarios
-- Generado con pg_dump a partir de `manage.py cargar_datos_prueba`.
-- Contraseña de todos los usuarios de prueba: Casimiro2026! (guardada con Argon2).
-- Ejecutar después de 01_esquema.sql sobre una base vacía.
-- La forma recomendada de recrear estos datos es: manage.py migrate && manage.py cargar_datos_prueba

--
-- PostgreSQL database dump
--

\restrict HwpjAlyO7VD9zBKNDiSMY1AKmrIyQDJYZqKtQcwu5LWggHRnzt9lDIXFU05oanH

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

INSERT INTO public.auth_group (id, name) VALUES (1, 'Administrador');
INSERT INTO public.auth_group (id, name) VALUES (2, 'Gerente');
INSERT INTO public.auth_group (id, name) VALUES (3, 'Cajero/Vendedor');
INSERT INTO public.auth_group (id, name) VALUES (4, 'Recursos Humanos');
INSERT INTO public.auth_group (id, name) VALUES (5, 'Encargado de almacén');
INSERT INTO public.auth_group (id, name) VALUES (6, 'Óptico/Técnico de taller');
INSERT INTO public.auth_group (id, name) VALUES (7, 'Empleado');


--
-- Data for Name: core_sucursal; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.core_sucursal (id, nombre, direccion, latitud, longitud, radio_metros, activa) VALUES (1, 'Sucursal Centro', 'Dirección de prueba 1, Sucre', -19.039699, -65.256900, 300, true);
INSERT INTO public.core_sucursal (id, nombre, direccion, latitud, longitud, radio_metros, activa) VALUES (2, 'Sucursal Norte', 'Dirección de prueba 2, Sucre', -19.033000, -65.262500, 150, true);


--
-- Data for Name: core_usuario; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (3, 'argon2$argon2id$v=19$m=102400,t=2,p=8$TnBhbXhMakZ6WklodTdrb0hlcWhqSw$iioOyySOv35KtGW1mFSdmIZPfxpl0CbrJ1fxpbIlssA', NULL, false, 'gerente', 'Daniel', 'Ortiz Paredes', 'gerente@opticascasimiro.test', false, true, '2026-10-12 07:43:00.056053-04', '1000002', false, 2, '70000002', 1);
INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (5, 'argon2$argon2id$v=19$m=102400,t=2,p=8$TkdpSW1MUXBTTDdCVXpWZXJ2WkJDNA$vYBsURyAdyWK6V9BmivPXJ4BoZ0fOdmJw7X4vu53z64', NULL, false, 'cajero2', 'Lucía', 'Quispe Vargas', 'cajero2@opticascasimiro.test', false, true, '2026-10-12 07:43:00.159373-04', '1000004', false, 3, '70000004', 2);
INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (6, 'argon2$argon2id$v=19$m=102400,t=2,p=8$aERqTkRJR1ZxcGFnN1NZTjM1bmRkaA$jHChMePgeF9hpU4mrigQcfvBHVZ3CcniKiX+Yw4VBYk', NULL, false, 'rrhh', 'Valeria', 'Ramos Soliz', 'rrhh@opticascasimiro.test', false, true, '2026-10-12 07:43:00.207804-04', '1000005', false, 4, '70000005', 1);
INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (7, 'argon2$argon2id$v=19$m=102400,t=2,p=8$TzlUOWs0SHpWZEpTVUVhOHIwQ2RQUw$omsxJGqZYlrT5uArweH4xocS6xjq83zUYTAv6+DSMuU', NULL, false, 'almacen', 'Pedro', 'Rojas Torrez', 'almacen@opticascasimiro.test', false, true, '2026-10-12 07:43:00.257653-04', '1000006', false, 5, '70000006', 1);
INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (8, 'argon2$argon2id$v=19$m=102400,t=2,p=8$MTltTTZ2bmM4TGRQWGlOQ25OZjB0cA$lvImFVRIWTGuX5zfewbGU303BJt/WcwoRIXCMqTKqfg', NULL, false, 'optico', 'Marta', 'Gutiérrez Choque', 'optico@opticascasimiro.test', false, true, '2026-10-12 07:43:00.306041-04', '1000007', false, 6, '70000007', 1);
INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (10, 'argon2$argon2id$v=19$m=102400,t=2,p=8$YjNBTndGbFdlOThZNU9nbE4zeU1Saw$ZnP/YwB9vSxkZuYqdqlbT1T4QImcENruc8s5gBYn+m8', NULL, false, 'empleado2', 'Ana', 'Mendoza Arce', 'empleado2@opticascasimiro.test', false, true, '2026-10-12 07:43:00.409735-04', '1000009', false, 7, '70000009', 2);
INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (11, 'argon2$argon2id$v=19$m=102400,t=2,p=8$SVJwR1pRSXhyakE3SzVaQTY3RVEzOA$Id6hyZV07w2/6PXaS/PxUlppGWMpDFzxNcOJl/E94+o', NULL, false, 'exempleado', 'Jorge', 'Salazar Ríos', 'exempleado@opticascasimiro.test', false, false, '2026-10-12 07:43:00.462193-04', '1000010', false, 7, '70000010', 1);
INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (4, 'argon2$argon2id$v=19$m=102400,t=2,p=8$UVFaSHp6VFptYnlNWkhEZ0ltWXJyMQ$wkoYl8CbXxAmX2lGMGD3ScCd1jaRqzsMu2TAZfijh4Y', '2026-10-12 07:47:00.126043-04', false, 'cajero1', 'Juan', 'Pérez Mamani', 'cajero1@opticascasimiro.test', false, true, '2026-10-12 07:43:00.107895-04', '1000003', false, 3, '70000003', 1);
INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (9, 'argon2$argon2id$v=19$m=102400,t=2,p=8$bDBSV2NBNTF3M01FSmExUk52cFNtZw$AaCarpWYlf71s0MAojXdq89N3Psqzk4Pn5iemuL37Mc', '2026-10-12 07:47:00.20999-04', false, 'empleado1', 'Luis', 'Fernández Cruz', 'empleado1@opticascasimiro.test', false, true, '2026-10-12 07:43:00.358825-04', '1000008', false, 7, '70000008', 1);
INSERT INTO public.core_usuario (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, ci, debe_cambiar_clave, rol_id, telefono, sucursal_id) VALUES (2, 'argon2$argon2id$v=19$m=102400,t=2,p=8$eWhSeTF4UklxVHpwMzlkcWtRVUpIMQ$vokQT/j7C2/HGmNacIrZCqjV4wTIITX5ixj5pZ43Lpg', '2026-10-12 07:47:00.046986-04', false, 'administrador', 'Sofía', 'Torrico Lima', 'administrador@opticascasimiro.test', false, true, '2026-10-12 07:42:59.800206-04', '1000001', false, 1, '70000001', 1);


--
-- Data for Name: asistencia_marcacion; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.asistencia_marcacion (id, tipo, fecha_hora, latitud, longitud, distancia_metros, sucursal_id, usuario_id) VALUES (1, 'ENTRADA', '2026-10-11 08:30:00-04', -19.039699, -65.256900, 0, 1, 9);
INSERT INTO public.asistencia_marcacion (id, tipo, fecha_hora, latitud, longitud, distancia_metros, sucursal_id, usuario_id) VALUES (2, 'SALIDA', '2026-10-11 12:30:00-04', -19.039699, -65.256900, 0, 1, 9);
INSERT INTO public.asistencia_marcacion (id, tipo, fecha_hora, latitud, longitud, distancia_metros, sucursal_id, usuario_id) VALUES (3, 'ENTRADA', '2026-10-11 14:30:00-04', -19.039699, -65.256900, 0, 1, 9);
INSERT INTO public.asistencia_marcacion (id, tipo, fecha_hora, latitud, longitud, distancia_metros, sucursal_id, usuario_id) VALUES (4, 'SALIDA', '2026-10-11 19:30:00-04', -19.039699, -65.256900, 0, 1, 9);


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.django_content_type (id, app_label, model) VALUES (1, 'admin', 'logentry');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (2, 'auth', 'group');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (3, 'auth', 'permission');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (5, 'sessions', 'session');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (6, 'core', 'usuario');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (7, 'core', 'registroactividad');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (8, 'core', 'sucursal');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (9, 'ventas', 'pago');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (10, 'ventas', 'venta');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (11, 'caja', 'movimientocaja');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (12, 'caja', 'sesioncaja');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (13, 'asistencia', 'marcacion');


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (5, 'Can add permission', 3, 'add_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (6, 'Can change permission', 3, 'change_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (7, 'Can delete permission', 3, 'delete_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (8, 'Can view permission', 3, 'view_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (9, 'Can add group', 2, 'add_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (10, 'Can change group', 2, 'change_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (11, 'Can delete group', 2, 'delete_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (12, 'Can view group', 2, 'view_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (13, 'Can add content type', 4, 'add_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (14, 'Can change content type', 4, 'change_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (15, 'Can delete content type', 4, 'delete_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (16, 'Can view content type', 4, 'view_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (17, 'Can add session', 5, 'add_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (18, 'Can change session', 5, 'change_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (19, 'Can delete session', 5, 'delete_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (20, 'Can view session', 5, 'view_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (21, 'Can add usuario', 6, 'add_usuario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (22, 'Can change usuario', 6, 'change_usuario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (23, 'Can delete usuario', 6, 'delete_usuario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (24, 'Can view usuario', 6, 'view_usuario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (25, 'Can add sucursal', 8, 'add_sucursal');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (26, 'Can change sucursal', 8, 'change_sucursal');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (27, 'Can delete sucursal', 8, 'delete_sucursal');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (28, 'Can view sucursal', 8, 'view_sucursal');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (29, 'Can add registro de actividad', 7, 'add_registroactividad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (30, 'Can change registro de actividad', 7, 'change_registroactividad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (31, 'Can delete registro de actividad', 7, 'delete_registroactividad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (32, 'Can view registro de actividad', 7, 'view_registroactividad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (33, 'Can add venta', 10, 'add_venta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (34, 'Can change venta', 10, 'change_venta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (35, 'Can delete venta', 10, 'delete_venta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (36, 'Can view venta', 10, 'view_venta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (37, 'Puede registrar ventas y cobrar pagos', 10, 'registrar_venta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (38, 'Puede ver las ventas de todos los vendedores', 10, 'ver_todas_ventas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (39, 'Can add pago', 9, 'add_pago');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (40, 'Can change pago', 9, 'change_pago');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (41, 'Can delete pago', 9, 'delete_pago');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (42, 'Can view pago', 9, 'view_pago');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (43, 'Can add sesión de caja', 12, 'add_sesioncaja');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (44, 'Can change sesión de caja', 12, 'change_sesioncaja');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (45, 'Can delete sesión de caja', 12, 'delete_sesioncaja');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (46, 'Can view sesión de caja', 12, 'view_sesioncaja');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (47, 'Puede abrir su caja, registrar movimientos y cerrarla', 12, 'operar_caja');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (48, 'Puede ver las cajas de todos los usuarios', 12, 'ver_todas_cajas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (49, 'Can add movimiento de caja', 11, 'add_movimientocaja');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (50, 'Can change movimiento de caja', 11, 'change_movimientocaja');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (51, 'Can delete movimiento de caja', 11, 'delete_movimientocaja');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (52, 'Can view movimiento de caja', 11, 'view_movimientocaja');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (53, 'Can add marcación', 13, 'add_marcacion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (54, 'Can change marcación', 13, 'change_marcacion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (55, 'Can delete marcación', 13, 'delete_marcacion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (56, 'Can view marcación', 13, 'view_marcacion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (57, 'Puede marcar su propia asistencia y ver su historial', 13, 'marcar_asistencia');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (58, 'Puede ver las marcaciones de todo el personal', 13, 'ver_todas_marcaciones');


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (1, 1, 32);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (2, 1, 58);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (3, 1, 37);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (4, 1, 38);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (5, 1, 47);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (6, 1, 48);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (7, 1, 21);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (8, 1, 22);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (9, 1, 24);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (10, 1, 25);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (11, 1, 26);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (12, 1, 28);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (13, 1, 57);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (14, 2, 32);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (15, 2, 38);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (16, 2, 48);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (17, 2, 24);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (18, 2, 57);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (19, 2, 58);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (20, 2, 28);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (21, 3, 57);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (22, 3, 37);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (23, 3, 47);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (24, 4, 24);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (25, 4, 57);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (26, 4, 58);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (27, 4, 28);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (28, 5, 57);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (29, 6, 57);
INSERT INTO public.auth_group_permissions (id, group_id, permission_id) VALUES (30, 7, 57);


--
-- Data for Name: caja_sesioncaja; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.caja_sesioncaja (id, estado, fecha_apertura, monto_inicial, fecha_cierre, monto_esperado, monto_contado, observacion, sucursal_id, usuario_id) VALUES (1, 'CERRADA', '2026-10-11 07:43:00.512819-04', 200.00, '2026-10-12 07:43:00.529925-04', 550.00, 550.00, '', 1, 4);


--
-- Data for Name: caja_movimientocaja; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.caja_movimientocaja (id, tipo, forma_pago, monto, concepto, fecha, usuario_id, sesion_id) VALUES (1, 'INGRESO', 'EFECTIVO', 350.00, 'Pago de la nota de venta 000001', '2026-10-12 07:43:00.517616-04', 4, 1);


--
-- Data for Name: core_usuario_groups; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (1, 2, 1);
INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (2, 3, 2);
INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (3, 4, 3);
INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (4, 5, 3);
INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (5, 6, 4);
INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (6, 7, 5);
INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (7, 8, 6);
INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (8, 9, 7);
INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (9, 10, 7);
INSERT INTO public.core_usuario_groups (id, usuario_id, group_id) VALUES (10, 11, 7);


--
-- Data for Name: ventas_venta; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.ventas_venta (id, fecha, cliente_nombre, cliente_ci, descripcion, total, estado, sucursal_id, vendedor_id) VALUES (1, '2026-10-12 07:43:00.514914-04', 'Cliente de prueba', '5555555', 'Armazón y lunas monofocales', 650.00, 'VIGENTE', 1, 4);


--
-- Data for Name: ventas_pago; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.ventas_pago (id, fecha, monto, forma_pago, movimiento_caja_id, usuario_id, venta_id) VALUES (1, '2026-10-12 07:43:00.519986-04', 350.00, 'EFECTIVO', 1, 4, 1);


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

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 30, true);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 58, true);


--
-- Name: caja_movimientocaja_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.caja_movimientocaja_id_seq', 1, true);


--
-- Name: caja_sesioncaja_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.caja_sesioncaja_id_seq', 1, true);


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

SELECT pg_catalog.setval('public.core_usuario_id_seq', 11, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 13, true);


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

\unrestrict HwpjAlyO7VD9zBKNDiSMY1AKmrIyQDJYZqKtQcwu5LWggHRnzt9lDIXFU05oanH


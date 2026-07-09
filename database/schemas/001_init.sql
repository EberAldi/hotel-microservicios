-- ============================================================
-- SISTEMA DE RESERVAS DE HOTEL - DATABASE-PER-SERVICE
-- 5 microservicios, 1 base de datos física + 1 rol dueño por servicio,
-- en la misma instancia de PostgreSQL (mismo servidor, distintas DBs).
-- Referencias ENTRE servicios = UUID lógico, SIN FK física.
--
-- Este script SOLO crea roles, bases y permisos. Las tablas de dominio
-- las crea cada servicio Django vía "python manage.py migrate" dentro
-- de SU propia base de datos.
-- ============================================================

CREATE ROLE svc_auth        LOGIN PASSWORD 'jicama1';
CREATE ROLE svc_catalog     LOGIN PASSWORD 'jicama2';
CREATE ROLE svc_reservation LOGIN PASSWORD 'jicama3';
CREATE ROLE svc_payment     LOGIN PASSWORD 'jicama4';
CREATE ROLE svc_review      LOGIN PASSWORD 'jicama5';

CREATE DATABASE auth_db        OWNER svc_auth;
CREATE DATABASE catalog_db     OWNER svc_catalog;
CREATE DATABASE reservation_db OWNER svc_reservation;
CREATE DATABASE payment_db     OWNER svc_payment;
CREATE DATABASE review_db      OWNER svc_review;

-- Postgres 15+: el owner de la BD no recibe automaticamente CREATE sobre
-- el schema "public" -- hay que darselo explicitamente o "migrate" falla.
\c auth_db
GRANT ALL ON SCHEMA public TO svc_auth;

\c catalog_db
GRANT ALL ON SCHEMA public TO svc_catalog;

\c reservation_db
GRANT ALL ON SCHEMA public TO svc_reservation;

\c payment_db
GRANT ALL ON SCHEMA public TO svc_payment;

\c review_db
GRANT ALL ON SCHEMA public TO svc_review;
-- ============================================================
-- SISTEMA DE RESERVAS DE HOTEL - SCHEMA EXACTO SEGÚN ER PROPORCIONADO
-- 5 microservicios, 1 schema + 1 rol por servicio en la misma instancia PostgreSQL.
-- Referencias ENTRE servicios = UUID lógico, SIN FK física (auth <-> catalog <-> reservation <-> payment <-> review)
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE SCHEMA IF NOT EXISTS auth_svc;
CREATE SCHEMA IF NOT EXISTS catalog_svc;
CREATE SCHEMA IF NOT EXISTS reservation_svc;
CREATE SCHEMA IF NOT EXISTS payment_svc;
CREATE SCHEMA IF NOT EXISTS review_svc;

-- ============================================================
-- 1. AUTH-SERVICE  (USERS, CUSTOMERS)
-- ============================================================
CREATE TABLE auth_svc.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(150) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20)  NOT NULL DEFAULT 'CUSTOMER', -- CUSTOMER, ADMIN, STAFF
    account_status  VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Relación "es": 1 usuario <-> 1 perfil de cliente (opcional, no todo user es customer, ej. staff)
CREATE TABLE auth_svc.customers (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL UNIQUE REFERENCES auth_svc.users(id) ON DELETE CASCADE,
    full_name           VARCHAR(150) NOT NULL,
    phone               VARCHAR(20),
    preferred_language  VARCHAR(10),
    loyalty_points      INT NOT NULL DEFAULT 0
);

-- ============================================================
-- 2. CATALOG-SERVICE  (ROOMS, SERVICES)
-- ============================================================
CREATE TABLE catalog_svc.rooms (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    number      VARCHAR(10) NOT NULL UNIQUE,
    type        VARCHAR(60) NOT NULL,
    base_price  NUMERIC(10,2) NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE'
);

CREATE TABLE catalog_svc.services (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(80) NOT NULL,
    category    VARCHAR(30) NOT NULL,
    price       NUMERIC(10,2) NOT NULL
);

-- ============================================================
-- 3. RESERVATION-SERVICE  (RESERVATIONS, RESERVATION_SERVICES)
-- ============================================================
CREATE TABLE reservation_svc.reservations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id     UUID NOT NULL,   -- ref. lógica -> auth_svc.customers.id
    room_id         UUID NOT NULL,   -- ref. lógica -> catalog_svc.rooms.id
    check_in        DATE NOT NULL,
    check_out       DATE NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, CONFIRMED, CANCELLED
    total_price     NUMERIC(10,2) NOT NULL,
    CHECK (check_out > check_in)
);

-- "incluye" / "es_incluido": tabla puente reservas <-> servicios
CREATE TABLE reservation_svc.reservation_services (
    reservation_id  UUID NOT NULL REFERENCES reservation_svc.reservations(id) ON DELETE CASCADE,
    service_id      UUID NOT NULL,   -- ref. lógica -> catalog_svc.services.id
    quantity        INT NOT NULL DEFAULT 1,
    PRIMARY KEY (reservation_id, service_id)
);

CREATE INDEX idx_reservations_room_dates ON reservation_svc.reservations (room_id, check_in, check_out);
CREATE INDEX idx_reservations_customer ON reservation_svc.reservations (customer_id);

-- ============================================================
-- 4. PAYMENT-SERVICE  (PAYMENTS)
-- ============================================================
CREATE TABLE payment_svc.payments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id  UUID NOT NULL,   -- ref. lógica -> reservation_svc.reservations.id
    amount          NUMERIC(10,2) NOT NULL,
    method          VARCHAR(20) NOT NULL,   -- CARD, PAYPAL, CASH
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, COMPLETED, FAILED, REFUNDED
    transaction_id  VARCHAR(150)
);

CREATE INDEX idx_payments_reservation ON payment_svc.payments (reservation_id);

-- ============================================================
-- 5. REVIEW-SERVICE  (REVIEWS)
--    "escribe": reseña polimórfica -> puede apuntar a ROOM, RESERVATION o SERVICE
--    (target_type + target_id), por eso no lleva FK física ni siquiera dentro
--    de su propio schema hacia esas entidades (viven en otros servicios).
-- ============================================================
CREATE TABLE review_svc.reviews (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id     UUID NOT NULL,   -- ref. lógica -> auth_svc.customers.id
    target_type     VARCHAR(20) NOT NULL,  -- ROOM, RESERVATION, SERVICE
    target_id       UUID NOT NULL,
    rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment         TEXT
);

CREATE INDEX idx_reviews_target ON review_svc.reviews (target_type, target_id);

-- ============================================================
-- 6. ROLES POR MICROSERVICIO
-- ============================================================
CREATE ROLE svc_auth        LOGIN PASSWORD 'CAMBIAR_ESTA_PASSWORD';
CREATE ROLE svc_catalog     LOGIN PASSWORD 'CAMBIAR_ESTA_PASSWORD';
CREATE ROLE svc_reservation LOGIN PASSWORD 'CAMBIAR_ESTA_PASSWORD';
CREATE ROLE svc_payment     LOGIN PASSWORD 'CAMBIAR_ESTA_PASSWORD';
CREATE ROLE svc_review      LOGIN PASSWORD 'CAMBIAR_ESTA_PASSWORD';

GRANT USAGE ON SCHEMA auth_svc TO svc_auth;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth_svc TO svc_auth;

GRANT USAGE ON SCHEMA catalog_svc TO svc_catalog;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA catalog_svc TO svc_catalog;
-- catalog es de lectura pública para reservation/payment/review (precios, disponibilidad)
GRANT USAGE ON SCHEMA catalog_svc TO svc_reservation, svc_payment, svc_review;
GRANT SELECT ON ALL TABLES IN SCHEMA catalog_svc TO svc_reservation, svc_payment, svc_review;

GRANT USAGE ON SCHEMA reservation_svc TO svc_reservation;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA reservation_svc TO svc_reservation;

GRANT USAGE ON SCHEMA payment_svc TO svc_payment;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA payment_svc TO svc_payment;

GRANT USAGE ON SCHEMA review_svc TO svc_review;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA review_svc TO svc_review;

-- auth_svc (contraseñas, datos personales) nadie más lo lee
REVOKE ALL ON SCHEMA auth_svc FROM svc_catalog, svc_reservation, svc_payment, svc_review;

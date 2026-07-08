# hotel-reservas (Django) — alineado al ER real

5 microservicios Django + DRF, 1 schema + 1 rol de Postgres por servicio,
mismo servidor físico. Estructura:

```
hotel-reservas/
├── docker-compose.yml
├── database/schemas/001_init.sql   # CREATE TABLE users, customers, rooms, services,
│                                    #   reservations, reservation_services, payments, reviews
└── services/
    ├── auth-service/            puerto 3001 · schema auth_svc
    │   └── accounts/            models: User, Customer
    ├── catalog-service/         puerto 3002 · schema catalog_svc
    │   └── rooms/ services_catalog/
    ├── reservation-service/     puerto 3003 · schema reservation_svc
    │   └── reservations/        models: Reservation, ReservationService
    ├── payment-service/         puerto 3004 · schema payment_svc
    │   └── payments/            models: Payment
    └── review-service/          puerto 3005 · schema review_svc
        └── reviews/             models: Review (polimórfica: target_type + target_id)
```

## Migraciones: cada servicio las suyas, la BD es una sola

La BD física es centralizada (un solo Postgres), pero cada servicio:
- solo tiene instaladas SUS apps en `INSTALLED_APPS` (nunca ve modelos de otro servicio),
- se conecta con SU rol dedicado, que solo tiene permiso de escritura sobre SU schema,
- corre `python manage.py makemigrations && python manage.py migrate` de forma
  completamente independiente, con su propia carpeta `migrations/` y su propio historial.

Nunca corras las migraciones de los 5 servicios "juntas" ni compartas una
carpeta `migrations/` entre ellos — eso rompería el aislamiento que ya
establece `001_init.sql` con los `GRANT`/`REVOKE` por rol.

## Levantar todo

1. Copia `.env.example` → `.env` en cada `services/<nombre>/` y ajusta passwords
   (deben coincidir con los roles del script SQL).
2. `docker compose up --build`
3. Dentro de cada servicio (o contenedor): `python manage.py migrate`

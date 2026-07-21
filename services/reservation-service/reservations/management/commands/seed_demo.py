import datetime

from django.core.management.base import BaseCommand

from reservations.models import Reservacion, ReservacionServicio, HistorialEstadoReservacion

# Estos UUID de cliente/habitacion/servicio deben coincidir EXACTAMENTE con
# los que crean auth-service/accounts/.../seed_demo.py y
# catalog-service/rooms/.../seed_demo.py -- no hay FK física entre
# microservicios, así que la referencia se sostiene "a mano" por convención.
CLIENTE_JUAN = "00000000-0000-0000-0000-000000000001"
CLIENTE_MARIA = "00000000-0000-0000-0000-000000000002"
CLIENTE_CARLOS = "00000000-0000-0000-0000-000000000003"

HAB_101 = "00000000-0000-0000-0000-000000000101"
HAB_102 = "00000000-0000-0000-0000-000000000102"
HAB_201 = "00000000-0000-0000-0000-000000000201"
HAB_301 = "00000000-0000-0000-0000-000000000301"

SERV_MASAJE = "00000000-0000-0000-0000-000000003001"
SERV_DESAYUNO = "00000000-0000-0000-0000-000000003002"

hoy = datetime.date.today()

RESERVACIONES = [
    {
        "id": "00000000-0000-0000-0000-000000004001",
        "cliente_id": CLIENTE_JUAN, "habitacion_id": HAB_101,
        "fecha_entrada": hoy - datetime.timedelta(days=2),
        "fecha_salida": hoy + datetime.timedelta(days=1),
        "estado": "confirmada", "precio_total": 2550,
    },
    {
        "id": "00000000-0000-0000-0000-000000004002",
        "cliente_id": CLIENTE_MARIA, "habitacion_id": HAB_201,
        "fecha_entrada": hoy + datetime.timedelta(days=5),
        "fecha_salida": hoy + datetime.timedelta(days=8),
        "estado": "pendiente_pago", "precio_total": 4350,
    },
    {
        "id": "00000000-0000-0000-0000-000000004003",
        "cliente_id": CLIENTE_JUAN, "habitacion_id": HAB_301,
        "fecha_entrada": hoy - datetime.timedelta(days=20),
        "fecha_salida": hoy - datetime.timedelta(days=17),
        "estado": "cancelada", "precio_total": 8400,
    },
    {
        "id": "00000000-0000-0000-0000-000000004004",
        "cliente_id": CLIENTE_CARLOS, "habitacion_id": HAB_102,
        "fecha_entrada": hoy + datetime.timedelta(days=1),
        "fecha_salida": hoy + datetime.timedelta(days=3),
        "estado": "confirmada", "precio_total": 1700,
    },
]

RESERVACION_SERVICIOS = [
    {"id": "00000000-0000-0000-0000-000000005001", "reservacion_id": RESERVACIONES[0]["id"],
     "servicio_id": SERV_DESAYUNO, "cantidad": 2, "precio_unitario": 180},
    {"id": "00000000-0000-0000-0000-000000005002", "reservacion_id": RESERVACIONES[0]["id"],
     "servicio_id": SERV_MASAJE, "cantidad": 1, "precio_unitario": 450},
    {"id": "00000000-0000-0000-0000-000000005003", "reservacion_id": RESERVACIONES[3]["id"],
     "servicio_id": SERV_DESAYUNO, "cantidad": 2, "precio_unitario": 180},
]


class Command(BaseCommand):
    """Crea reservaciones de prueba (con su historial de estado y algunos
    servicios contratados). Idempotente: IDs fijos + get_or_create."""
    help = "Crea reservaciones de prueba (idempotente)."

    def handle(self, *args, **options):
        creadas = 0
        for datos in RESERVACIONES:
            reservacion, fue_creada = Reservacion.objects.get_or_create(
                id=datos["id"],
                defaults={
                    "cliente_id": datos["cliente_id"],
                    "habitacion_id": datos["habitacion_id"],
                    "fecha_entrada": datos["fecha_entrada"],
                    "fecha_salida": datos["fecha_salida"],
                    "estado": datos["estado"],
                    "precio_total": datos["precio_total"],
                },
            )
            if fue_creada:
                creadas += 1
                HistorialEstadoReservacion.objects.create(
                    reservacion=reservacion, estado_anterior="", estado_nuevo=reservacion.estado,
                    motivo="Reservación de prueba (seed_demo)",
                )

        for datos in RESERVACION_SERVICIOS:
            ReservacionServicio.objects.get_or_create(
                id=datos["id"],
                defaults={
                    "reservacion_id": datos["reservacion_id"],
                    "servicio_id": datos["servicio_id"],
                    "cantidad": datos["cantidad"],
                    "precio_unitario": datos["precio_unitario"],
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"Reservaciones de prueba listas ({creadas} nuevas, {len(RESERVACIONES) - creadas} ya existían)."
        ))

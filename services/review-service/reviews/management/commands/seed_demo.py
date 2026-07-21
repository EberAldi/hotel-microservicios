from django.core.management.base import BaseCommand

from reviews.models import Resena

# Estos UUID de cliente/habitacion/servicio deben coincidir EXACTAMENTE con
# los que crean auth-service/accounts/.../seed_demo.py y
# catalog-service/rooms/.../seed_demo.py -- no hay FK física entre
# microservicios, así que la referencia se sostiene "a mano" por convención.
CLIENTE_JUAN = "00000000-0000-0000-0000-000000000001"
CLIENTE_MARIA = "00000000-0000-0000-0000-000000000002"
CLIENTE_CARLOS = "00000000-0000-0000-0000-000000000003"

HAB_101 = "00000000-0000-0000-0000-000000000101"
HAB_301 = "00000000-0000-0000-0000-000000000301"

SERV_MASAJE = "00000000-0000-0000-0000-000000003001"
SERV_DESAYUNO = "00000000-0000-0000-0000-000000003002"

RESENAS = [
    {"id": "00000000-0000-0000-0000-000000006001", "cliente_id": CLIENTE_JUAN,
     "tipo_objetivo": "HABITACION", "objetivo_id": HAB_101, "calificacion": 5,
     "comentario": "Excelente habitación, muy limpia y cómoda.", "estado": "aprobada"},
    {"id": "00000000-0000-0000-0000-000000006002", "cliente_id": CLIENTE_MARIA,
     "tipo_objetivo": "HABITACION", "objetivo_id": HAB_301, "calificacion": 4,
     "comentario": "La suite es hermosa, aunque el aire acondicionado hacía ruido.", "estado": "aprobada"},
    {"id": "00000000-0000-0000-0000-000000006003", "cliente_id": CLIENTE_CARLOS,
     "tipo_objetivo": "SERVICIO", "objetivo_id": SERV_MASAJE, "calificacion": 5,
     "comentario": "El masaje fue justo lo que necesitaba después del viaje.", "estado": "aprobada"},
    {"id": "00000000-0000-0000-0000-000000006004", "cliente_id": CLIENTE_JUAN,
     "tipo_objetivo": "SERVICIO", "objetivo_id": SERV_DESAYUNO, "calificacion": 3,
     "comentario": "El desayuno estuvo bien, pero tardaron en atendernos.", "estado": "aprobada"},
    {"id": "00000000-0000-0000-0000-000000006005", "cliente_id": CLIENTE_MARIA,
     "tipo_objetivo": "HABITACION", "objetivo_id": HAB_101, "calificacion": 1,
     "comentario": "Reseña de prueba pendiente de moderar.", "estado": "oculta"},
]


class Command(BaseCommand):
    """Crea reseñas de prueba (algunas aprobadas, una oculta para poder
    probar la moderación). Idempotente: IDs fijos + get_or_create."""
    help = "Crea reseñas de prueba (idempotente)."

    def handle(self, *args, **options):
        creadas = 0
        for datos in RESENAS:
            _, fue_creada = Resena.objects.get_or_create(
                id=datos["id"],
                defaults={
                    "cliente_id": datos["cliente_id"],
                    "tipo_objetivo": datos["tipo_objetivo"],
                    "objetivo_id": datos["objetivo_id"],
                    "calificacion": datos["calificacion"],
                    "comentario": datos["comentario"],
                    "estado": datos["estado"],
                },
            )
            if fue_creada:
                creadas += 1

        self.stdout.write(self.style.SUCCESS(
            f"Reseñas de prueba listas ({creadas} nuevas, {len(RESENAS) - creadas} ya existían)."
        ))

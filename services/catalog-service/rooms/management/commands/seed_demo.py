from django.core.management.base import BaseCommand

from rooms.models import TipoHabitacion, Habitacion
from services_catalog.models import CategoriaServicio, Servicio

# IDs fijos a propósito: reservation-service y review-service referencian
# estos MISMOS UUID de habitación/servicio en sus propios seed_demo -- como
# no hay FK física entre microservicios, todos deben coincidir "a mano".
TIPOS = [
    {"id": "00000000-0000-0000-0000-000000001001", "nombre": "Individual",
     "descripcion": "Habitación para una persona.", "capacidad_maxima": 1},
    {"id": "00000000-0000-0000-0000-000000001002", "nombre": "Doble",
     "descripcion": "Habitación con cama matrimonial o dos camas.", "capacidad_maxima": 2},
    {"id": "00000000-0000-0000-0000-000000001003", "nombre": "Suite",
     "descripcion": "Suite amplia con sala de estar separada.", "capacidad_maxima": 4},
]

HABITACIONES = [
    {"id": "00000000-0000-0000-0000-000000000101", "numero": "101",
     "tipo_id": TIPOS[0]["id"], "precio_base": 850, "estado": "disponible"},
    {"id": "00000000-0000-0000-0000-000000000102", "numero": "102",
     "tipo_id": TIPOS[0]["id"], "precio_base": 850, "estado": "disponible"},
    {"id": "00000000-0000-0000-0000-000000000201", "numero": "201",
     "tipo_id": TIPOS[1]["id"], "precio_base": 1450, "estado": "disponible"},
    {"id": "00000000-0000-0000-0000-000000000202", "numero": "202",
     "tipo_id": TIPOS[1]["id"], "precio_base": 1450, "estado": "mantenimiento"},
    {"id": "00000000-0000-0000-0000-000000000301", "numero": "301",
     "tipo_id": TIPOS[2]["id"], "precio_base": 2800, "estado": "disponible"},
]

CATEGORIAS = [
    {"id": "00000000-0000-0000-0000-000000002001", "nombre": "Spa y bienestar",
     "descripcion": "Servicios de relajación y cuidado personal."},
    {"id": "00000000-0000-0000-0000-000000002002", "nombre": "Alimentos y bebidas",
     "descripcion": "Servicios de comida y bebida dentro del hotel."},
    {"id": "00000000-0000-0000-0000-000000002003", "nombre": "Transporte",
     "descripcion": "Traslados y transporte para huéspedes."},
]

SERVICIOS = [
    {"id": "00000000-0000-0000-0000-000000003001", "nombre": "Masaje relajante",
     "categoria_id": CATEGORIAS[0]["id"], "precio": 450},
    {"id": "00000000-0000-0000-0000-000000003002", "nombre": "Desayuno buffet",
     "categoria_id": CATEGORIAS[1]["id"], "precio": 180},
    {"id": "00000000-0000-0000-0000-000000003003", "nombre": "Traslado aeropuerto",
     "categoria_id": CATEGORIAS[2]["id"], "precio": 350},
]


class Command(BaseCommand):
    """Crea tipos de habitación, habitaciones, categorías y servicios de
    prueba. Idempotente: IDs fijos + get_or_create, seguro en cada arranque."""
    help = "Crea catálogo de prueba (tipos, habitaciones, categorías, servicios)."

    def handle(self, *args, **options):
        for datos in TIPOS:
            TipoHabitacion.objects.get_or_create(id=datos["id"], defaults={
                "nombre": datos["nombre"], "descripcion": datos["descripcion"],
                "capacidad_maxima": datos["capacidad_maxima"],
            })

        for datos in HABITACIONES:
            Habitacion.objects.get_or_create(id=datos["id"], defaults={
                "numero": datos["numero"], "tipo_id": datos["tipo_id"],
                "precio_base": datos["precio_base"], "estado": datos["estado"],
            })

        for datos in CATEGORIAS:
            CategoriaServicio.objects.get_or_create(id=datos["id"], defaults={
                "nombre": datos["nombre"], "descripcion": datos["descripcion"],
            })

        for datos in SERVICIOS:
            Servicio.objects.get_or_create(id=datos["id"], defaults={
                "nombre": datos["nombre"], "categoria_id": datos["categoria_id"],
                "precio": datos["precio"],
            })

        self.stdout.write(self.style.SUCCESS(
            f"Catálogo de prueba listo: {len(TIPOS)} tipos, {len(HABITACIONES)} habitaciones, "
            f"{len(CATEGORIAS)} categorías, {len(SERVICIOS)} servicios."
        ))

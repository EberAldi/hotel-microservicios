from django.core.management.base import BaseCommand

from accounts.models import Usuario, Cliente

# IDs fijos (no aleatorios) a propósito: reservation-service y review-service
# usan estos MISMOS UUID de cliente en sus propios seed_demo -- como no hay
# FK física entre microservicios, todos deben coincidir "a mano".
CLIENTES = [
    {
        "usuario_id": "00000000-0000-0000-0000-0000000000a1",
        "cliente_id": "00000000-0000-0000-0000-000000000001",
        "correo": "juan.perez@example.com",
        "password": "cliente123",
        "nombre_completo": "Juan Pérez",
        "telefono": "9511234567",
    },
    {
        "usuario_id": "00000000-0000-0000-0000-0000000000a2",
        "cliente_id": "00000000-0000-0000-0000-000000000002",
        "correo": "maria.lopez@example.com",
        "password": "cliente123",
        "nombre_completo": "María López",
        "telefono": "9517654321",
    },
    {
        "usuario_id": "00000000-0000-0000-0000-0000000000a3",
        "cliente_id": "00000000-0000-0000-0000-000000000003",
        "correo": "carlos.ramirez@example.com",
        "password": "cliente123",
        "nombre_completo": "Carlos Ramírez",
        "telefono": "9519876543",
    },
]


class Command(BaseCommand):
    """
    Crea usuarios "cliente" de prueba (con su perfil de Cliente) para poder
    ver datos reales en el panel admin sin depender de que alguien se
    registre a mano. Idempotente: se puede correr en cada arranque del
    contenedor sin duplicar (usa IDs fijos + get_or_create).
    """
    help = "Crea usuarios/clientes de prueba (idempotente)."

    def handle(self, *args, **options):
        creados = 0
        for datos in CLIENTES:
            usuario, fue_creado = Usuario.objects.get_or_create(
                id=datos["usuario_id"],
                defaults={
                    "correo": datos["correo"],
                    "rol": "cliente",
                    "estado_cuenta": "activo",
                },
            )
            if fue_creado:
                usuario.set_password(datos["password"])
                usuario.save(update_fields=["password"])
                creados += 1

            Cliente.objects.get_or_create(
                id=datos["cliente_id"],
                defaults={
                    "usuario": usuario,
                    "nombre_completo": datos["nombre_completo"],
                    "telefono": datos["telefono"],
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"Clientes de prueba listos ({creados} nuevos, {len(CLIENTES) - creados} ya existían)."
        ))

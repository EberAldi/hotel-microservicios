from django.core.management.base import BaseCommand
from django.conf import settings

from accounts.models import Usuario


class Command(BaseCommand):
    """
    Crea el usuario admin inicial si no existe todavia (idempotente -- se
    puede correr en cada arranque del contenedor sin duplicar ni romper nada).

    Lee las credenciales de variables de entorno (ADMIN_EMAIL, ADMIN_PASSWORD)
    para no dejar contraseñas hardcodeadas en el codigo.
    """
    help = 'Crea el usuario admin inicial a partir de ADMIN_EMAIL/ADMIN_PASSWORD si no existe.'

    def handle(self, *args, **options):
        correo = getattr(settings, 'ADMIN_EMAIL', None)
        contrasena = getattr(settings, 'ADMIN_PASSWORD', None)

        if not correo or not contrasena:
            self.stdout.write(self.style.WARNING(
                'ADMIN_EMAIL o ADMIN_PASSWORD no configurados en .env -- se omite creacion de admin.'
            ))
            return

        usuario, creado = Usuario.objects.get_or_create(
            correo=correo,
            defaults={'rol': 'admin', 'estado_cuenta': 'activo'},
        )
        if creado:
            # set_password usa el hasher de Django (no bcrypt crudo), que es
            # lo que Usuario.check_password() sabe verificar en el login.
            usuario.set_password(contrasena)
            usuario.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'Admin creado: {correo}'))
        elif usuario.rol != 'admin':
            usuario.rol = 'admin'
            usuario.save(update_fields=['rol'])
            self.stdout.write(self.style.SUCCESS(f'Usuario existente promovido a admin: {correo}'))
        else:
            self.stdout.write(f'Admin ya existia, sin cambios: {correo}')
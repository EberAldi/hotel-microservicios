import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'reviews',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# Este servicio migra SOLO sus propias apps (ver INSTALLED_APPS arriba).
# Se conecta a SU PROPIA base de datos (review_db) con SU PROPIO rol (svc_review),
# dueño exclusivo de esa base -- database-per-service real, no schemas
# compartidos. Cada servicio corre "python manage.py migrate" de forma
# totalmente independiente sobre su propia base de datos.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# DB_SCHEMA es opcional: solo se usa en desarrollo local, cuando los 5
# servicios comparten una sola base fisica ("hotel-desarrollodeservicios")
# con un esquema Postgres por servicio. En docker-compose/produccion cada
# servicio tiene su propia base (esquema "public" por defecto) y no hace falta.
if os.getenv('DB_SCHEMA'):
    DATABASES['default']['OPTIONS'] = {'options': f"-c search_path={os.getenv('DB_SCHEMA')},public"}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'reviews.authentication.JWTRolAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY', SECRET_KEY),
}

# Usados por reviews.authentication.JWTRolAuthentication para decodificar el
# access token que emite auth-service (mismo secreto/algoritmo en los 5 servicios).
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
JWT_ALGORITHM = 'HS256'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "False") == "True"
CORS_ALLOWED_ORIGINS = [o for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if o]
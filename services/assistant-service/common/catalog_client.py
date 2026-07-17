import requests
from django.conf import settings


def buscar_habitaciones(tipo_nombre=None):
    """Consulta catalog-service (publico, sin auth) para habitaciones disponibles."""
    url = f"{settings.CATALOG_SERVICE_URL}/api/catalogo/habitaciones/?estado=disponible"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        habitaciones = response.json()
    except requests.RequestException:
        return []
    if tipo_nombre:
        habitaciones = [h for h in habitaciones if tipo_nombre.lower() in h.get('tipo_nombre', '').lower()]
    return habitaciones


def buscar_servicios(categoria_nombre=None):
    """Consulta catalog-service (publico, sin auth) para servicios extra."""
    url = f"{settings.CATALOG_SERVICE_URL}/api/catalogo/servicios/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        servicios = response.json()
    except requests.RequestException:
        return []
    if categoria_nombre:
        servicios = [s for s in servicios if categoria_nombre.lower() in s.get('categoria_nombre', '').lower()]
    return servicios
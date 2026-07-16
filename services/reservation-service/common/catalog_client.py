import requests
from django.conf import settings
from rest_framework.exceptions import APIException, NotFound


class CatalogServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'catalog-service no esta disponible en este momento. Intenta de nuevo mas tarde.'
    default_code = 'catalog_service_unavailable'


def obtener_servicio(servicio_id):
    """
    Consulta catalog-service para validar que un servicio existe y traer
    su precio actual -- es la fuente de verdad del precio, nunca se confia
    en lo que mande el cliente en el body.
    """
    url = f"{settings.CATALOG_SERVICE_URL}/api/catalogo/servicios/{servicio_id}/"
    try:
        response = requests.get(url, timeout=3)
    except requests.RequestException:
        raise CatalogServiceUnavailable()

    if response.status_code == 404:
        raise NotFound(f'El servicio {servicio_id} no existe en el catalogo.')
    if response.status_code != 200:
        raise CatalogServiceUnavailable()

    return response.json()
import requests
from django.conf import settings
from rest_framework.exceptions import APIException, NotFound, PermissionDenied


class ReservationServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'reservation-service no esta disponible en este momento. Intenta de nuevo mas tarde.'
    default_code = 'reservation_service_unavailable'


def _verificar(url, auth_header):
    """
    Reenvia el MISMO token del cliente a reservation-service. Como esos
    endpoints ya tienen su propia verificacion de ownership (cliente ve
    solo lo suyo, admin ve todo), un 200 aqui ya confirma que el recurso
    existe Y le pertenece a quien esta pagando -- no se duplica esa logica.
    """
    if not auth_header:
        raise PermissionDenied('Falta el token de autorizacion para verificar el recurso.')
    try:
        response = requests.get(url, headers={'Authorization': auth_header}, timeout=3)
    except requests.RequestException:
        raise ReservationServiceUnavailable()

    if response.status_code == 404:
        raise NotFound('El recurso indicado no existe en reservation-service.')
    if response.status_code == 403:
        raise PermissionDenied('Ese recurso no te pertenece.')
    if response.status_code != 200:
        raise ReservationServiceUnavailable()
    return response.json()


def verificar_reservacion(reservacion_id, auth_header):
    url = f"{settings.RESERVATION_SERVICE_URL}/api/reservaciones/reservaciones/{reservacion_id}/"
    return _verificar(url, auth_header)


def verificar_carrito(carrito_id, auth_header):
    url = f"{settings.RESERVATION_SERVICE_URL}/api/reservaciones/carritos/{carrito_id}/"
    return _verificar(url, auth_header)
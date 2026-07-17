import requests
from django.conf import settings


def consultar_mis_reservaciones(auth_header):
    """
    Reenvia el token del cliente a reservation-service. Ese endpoint ya
    filtra automaticamente por dueño (un cliente solo ve las suyas), asi
    que no hace falta ninguna logica de ownership extra aqui.
    """
    if not auth_header:
        return []
    url = f"{settings.RESERVATION_SERVICE_URL}/api/reservaciones/reservaciones/"
    try:
        response = requests.get(url, headers={'Authorization': auth_header}, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []
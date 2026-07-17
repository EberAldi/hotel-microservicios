import requests
from rest_framework.exceptions import APIException, NotFound


class ClimaServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'El servicio de clima no esta disponible en este momento.'
    default_code = 'clima_service_unavailable'


def geocodificar_ciudad(ciudad):
    """Open-Meteo Geocoding API -- gratis, sin API key."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    try:
        response = requests.get(url, params={'name': ciudad, 'count': 1, 'language': 'es'}, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        raise ClimaServiceUnavailable()

    resultados = response.json().get('results')
    if not resultados:
        raise NotFound(f"No se encontro la ciudad '{ciudad}'.")

    lugar = resultados[0]
    return {
        'nombre': lugar['name'],
        'pais': lugar.get('country', ''),
        'lat': lugar['latitude'],
        'lon': lugar['longitude'],
    }


def obtener_pronostico(lat, lon, fecha=None):
    """Open-Meteo Forecast API -- gratis, sin API key. fecha en formato YYYY-MM-DD, opcional."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode',
        'timezone': 'auto',
    }
    if fecha:
        params['start_date'] = fecha
        params['end_date'] = fecha

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        raise ClimaServiceUnavailable()

    datos = response.json().get('daily', {})
    if not datos.get('time'):
        raise ClimaServiceUnavailable()

    return {
        'fecha': datos['time'][0],
        'temp_maxima': datos['temperature_2m_max'][0],
        'temp_minima': datos['temperature_2m_min'][0],
        'probabilidad_lluvia': datos['precipitation_probability_max'][0],
    }
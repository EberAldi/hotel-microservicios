from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from common.permissions import EsClienteOAdmin
from .weather_client import geocodificar_ciudad, obtener_pronostico
from .gemini_client import generar_recomendacion_clima, responder_chat


class ClimaView(APIView):
    """
    POST /api/asistente/clima/   body: {"ciudad": "Cancun", "fecha": "2026-08-01"}
    Publico, sin login. 'fecha' es opcional (default: hoy).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        ciudad = request.data.get('ciudad')
        fecha = request.data.get('fecha')
        if not ciudad:
            return Response({'detail': 'ciudad es requerida.'}, status=400)

        lugar = geocodificar_ciudad(ciudad)
        pronostico = obtener_pronostico(lugar['lat'], lugar['lon'], fecha)
        recomendacion = generar_recomendacion_clima(lugar['nombre'], pronostico)

        return Response({
            'ciudad': lugar['nombre'],
            'pais': lugar['pais'],
            'pronostico': pronostico,
            'recomendacion': recomendacion,
        })


class ChatView(APIView):
    """
    POST /api/asistente/chat/   body: {"mensaje": "..."}
    Requiere JWT (cliente o admin).
    """
    permission_classes = [EsClienteOAdmin]

    def post(self, request):
        mensaje = request.data.get('mensaje')
        if not mensaje:
            return Response({'detail': 'mensaje es requerido.'}, status=400)

        auth_header = request.META.get('HTTP_AUTHORIZATION')
        respuesta = responder_chat(mensaje, auth_header)
        return Response({'respuesta': respuesta})
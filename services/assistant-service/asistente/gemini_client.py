import json
from pathlib import Path

import google.generativeai as genai
from django.conf import settings
from rest_framework.exceptions import APIException

from common.catalog_client import buscar_habitaciones, buscar_servicios
from common.reservation_client import consultar_mis_reservaciones

genai.configure(api_key=settings.GEMINI_API_KEY)

RUTA_INFO_HOTEL = Path(__file__).resolve().parent / 'info_hotel.json'


class IAServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'El asistente de IA no esta disponible en este momento.'
    default_code = 'ia_service_unavailable'


def _cargar_info_hotel():
    """
    Lee la info fija del hotel desde info_hotel.json en cada llamada
    (el archivo es chico, no vale la pena cachearlo en memoria).
    Si el archivo tiene un error de formato, no tumba el servicio --
    simplemente el chat responde sin ese contexto extra.
    """
    try:
        with open(RUTA_INFO_HOTEL, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def generar_recomendacion_clima(ciudad, pronostico):
    prompt = (
        f"Eres el asistente de un hotel. El pronostico para {ciudad} el dia "
        f"{pronostico['fecha']} es: temperatura entre {pronostico['temp_minima']} y "
        f"{pronostico['temp_maxima']} grados Celsius, con {pronostico['probabilidad_lluvia']}% "
        f"de probabilidad de lluvia. Da una recomendacion breve (maximo 2 lineas, en español) "
        f"para un huesped del hotel sobre que actividades o servicios le convendrian ese dia "
        f"(ej. spa si va a llover, alberca/excursion si hace buen clima)."
    )
    try:
        modelo = genai.GenerativeModel(settings.GEMINI_MODEL)
        respuesta = modelo.generate_content(prompt)
        return respuesta.text.strip()
    except Exception:
        raise IAServiceUnavailable()


HERRAMIENTAS = [
    {
        'function_declarations': [
            {
                'name': 'buscar_habitaciones',
                'description': 'Busca habitaciones disponibles del hotel, opcionalmente filtradas por tipo (ej. Suite).',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'tipo_nombre': {'type': 'string', 'description': 'Nombre del tipo de habitacion a buscar (opcional)'},
                    },
                },
            },
            {
                'name': 'buscar_servicios',
                'description': 'Busca servicios extra del hotel (spa, transporte, excursiones), opcionalmente filtrados por categoria.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'categoria_nombre': {'type': 'string', 'description': 'Nombre de la categoria a buscar (opcional)'},
                    },
                },
            },
            {
                'name': 'consultar_mis_reservaciones',
                'description': (
                    'Consulta las reservaciones del cliente que esta usando el chat en este '
                    'momento (nunca de otro cliente). Usar cuando pregunten por "mi reservacion", '
                    '"cuando llego", "mi estadia", estado de pago, fechas, etc.'
                ),
                'parameters': {'type': 'object', 'properties': {}},
            },
        ]
    }
]


def _instruccion_sistema():
    info = _cargar_info_hotel()
    return (
        "Eres el asistente virtual de un hotel. Respondes preguntas de huespedes "
        "de forma breve, amable y en español.\n\n"
        "REGLA ESTRICTA: solo respondes preguntas relacionadas con el hotel "
        "(habitaciones, servicios, reservaciones, politicas, instalaciones, "
        "horarios, pagos). Si te preguntan CUALQUIER cosa fuera de ese tema "
        "(matemáticas, noticias, opiniones personales, otros temas generales, "
        "chistes, etc.), responde exactamente: 'Solo puedo ayudarte con "
        "preguntas relacionadas con el hotel. ¿Hay algo sobre tu estadia o "
        "nuestros servicios en lo que te pueda ayudar?' y no respondas nada mas "
        "de esa otra pregunta.\n\n"
        f"Informacion fija del hotel (JSON):\n{json.dumps(info, ensure_ascii=False, indent=2)}\n\n"
        "Si te preguntan por habitaciones o servicios disponibles, usa "
        "'buscar_habitaciones' o 'buscar_servicios' para dar informacion real "
        "y actualizada, no inventes precios ni disponibilidad. Si preguntan "
        "por SU reservacion, usa 'consultar_mis_reservaciones'."
    )


def responder_chat(mensaje_usuario, auth_header):
    try:
        modelo = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            tools=HERRAMIENTAS,
            system_instruction=_instruccion_sistema(),
        )
        chat = modelo.start_chat()
        respuesta = chat.send_message(mensaje_usuario)

        while respuesta.candidates[0].content.parts[0].function_call.name:
            llamada = respuesta.candidates[0].content.parts[0].function_call
            nombre = llamada.name
            argumentos = dict(llamada.args)

            if nombre == 'buscar_habitaciones':
                resultado = buscar_habitaciones(argumentos.get('tipo_nombre'))
            elif nombre == 'buscar_servicios':
                resultado = buscar_servicios(argumentos.get('categoria_nombre'))
            elif nombre == 'consultar_mis_reservaciones':
                resultado = consultar_mis_reservaciones(auth_header)
            else:
                resultado = []

            respuesta = chat.send_message(
                genai.protos.Content(
                    parts=[genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=nombre, response={'resultado': resultado}
                        )
                    )]
                )
            )

        return respuesta.text.strip()
    except Exception:
        raise IAServiceUnavailable()
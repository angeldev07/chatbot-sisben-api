import os
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from .utils import SecretariaDesarrollo
from sisben.utils.get_sisben_fns import validateDoc
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import permission_classes
from shared.auth.apikey import APIKeyPermission


@swagger_auto_schema(
    tags=['Secretaria de Desarrollo'],
    methods=('get', 'post'),
    operation_description="Consulta si el usuario existe en el RUD y retorna el certificado",
    manual_parameters=[
        openapi.Parameter(
            'cedula', 
            openapi.IN_QUERY, 
            description="Número de documento de la persona", 
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'apiKey', 
            openapi.IN_QUERY, 
            description="Api key para autenticar la consulta", 
            type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: openapi.Response
        (
            description="Respuesta exitosa",
            examples={
                "application/json": {
                    "mensaje":'http://localhost:8000/media/certificadogrud-1234567890.pdf' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}/media/certificado-grud-1234567890.pdf'
                }
            },
        ), 
        400: openapi.Response
        (
            description="Se envia un mensaje de error dependiendo de lo que salga mal en la consulta", 
            examples={
                "application/json": {
                    "mensaje": [
                        "El tipo de documento es requerido",
                        "El número de documento no es válido",
                        "Error al obtener el certificado de la secretaria de desarrollo"
                    ]
                }
            }
        ), 
    }
)
@api_view(["POST", "GET"])
@permission_classes([APIKeyPermission])
def getungrudcertificate(request: Request):
    """
    Método que obtiene el certificado de la secretaria de desarrollo
    """

    cedula = request.query_params.get("cedula")

    if not cedula:
        return Response({"mensaje": "El número de documento es requerido"}, status=400)

    if not validateDoc(cedula):
        return Response({"mensaje": "El número de documento no es válido"}, status=400)

    secretaria = SecretariaDesarrollo()
    return Response(secretaria.getungrudcertificate(cedula))

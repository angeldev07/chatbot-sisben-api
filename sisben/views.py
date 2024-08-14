from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from sisben.helpers.session import SisbenSession
from sisben.utils.get_sisben_fns import validateParams, generar_pdf
from shared.auth.apikey import APIKeyPermission

import os 

@swagger_auto_schema(
    tags=['Sisben'],
    methods=('get', 'post'),
    operation_description="Consulta el Sisben de una persona por su tipo y número de documento",
    manual_parameters=[
        openapi.Parameter(
            'docType', 
            openapi.IN_QUERY, 
            description=(
                """
                    Tipo de documento de la persona. 
                    1. Registro Civil
                    2. Tarjeta de Identidad 
                    3. Cédula de Ciudadanía 
                    4. Cédula de Extranjería 
                    5. DNI (Pais de origen) 
                    6. DNI (Pasaporte) 
                    7. Salvoconducto para refugiado 
                    8. Permiso Especial de Permanencia 
                    0. Permiso Por Protección Tempora
                """
            ),
            type=openapi.TYPE_STRING,
            enum=[str(i) for i in range(1, 10)]
        ),
        openapi.Parameter(
            'numDoc', 
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
                    "mensaje":'http://localhost:8000/media/sisben/1234567890.pdf' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}/media/1234567890.pdf'
                }
            },
        ), 
        400: openapi.Response
        (
            description="Se envia un mensaje de error dependiendo de lo que salga mal en la consulta", 
            examples={
                "application/json": {
                    "mensaje": [
                        "El tipo de documento no es válido",
                        "El número de documento no es válido",
                        "Lo sentimos, la pagina del Sisben no responde en este momento. Por favor, intenta de nuevo mas tarde."
                    ]
                }
            }
        ), 
    }
)
@api_view(['GET', 'POST'])
@permission_classes([APIKeyPermission])
def sisben(request: Request):
    try:
        # Obtiene el tipo de documento y el número de documento de la consulta
        docType = request.query_params.get('docType')
        numDoc = request.query_params.get('numDoc')

        session = SisbenSession()

        # Valida los parámetros de entrada
        validateParams(docType, numDoc, session.get_types_document())

        data = session.get_sisben(docType, numDoc)
        
        context = {
            'persona': data['persona'],
            'sisben': data['sisben'],
            'contacto': data['contacto']
        }

        # Genera el PDF de la consulta del Sisben
        download_url = generar_pdf(request, context, numDoc)

        #Obtiene la url de acceso al pdf. 
        data['download_url'] = f'http://localhost:8000{download_url}' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}{download_url}'
        session.close_session()
        return Response({ 'mensaje': f'{data['download_url']}' } , status=200, content_type='application/json')
    except ValueError as ve:
        session.close_session()
        return Response({'mensaje': str(ve)}, status=200, content_type='application/json')
    except Exception as e:
        session.close_session()
        return Response( { 'mensaje': str(e) }, status=200, content_type='application/json')
    
@swagger_auto_schema(
    tags=['Sisben'],
    methods=('get', 'post'),
    operation_description="Valida si una persona existe en el Sisben de Villa del Rosario",
    manual_parameters=[
        openapi.Parameter(
            'docType', 
            openapi.IN_QUERY, 
            description=(
                """
                    Tipo de documento de la persona. 
                    1. Registro Civil
                    2. Tarjeta de Identidad 
                    3. Cédula de Ciudadanía 
                    4. Cédula de Extranjería 
                    5. DNI (Pais de origen) 
                    6. DNI (Pasaporte) 
                    7. Salvoconducto para refugiado 
                    8. Permiso Especial de Permanencia 
                    0. Permiso Por Protección Tempora
                """
            ),
            type=openapi.TYPE_STRING,
            enum=[str(i) for i in range(1, 10)]
        ),
        openapi.Parameter(
            'numDoc', 
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
                    "mensaje": [
                        'Existe',
                        'Existe, pero no en Villa del Rosario',
                        'No existe en el sisben.'
                    ]
                }
            },
        ), 
        400: openapi.Response
        (
            description="Se envia un mensaje de error dependiendo de lo que salga mal en la consulta", 
            examples={
                "application/json": {
                    "mensaje": [
                        "El tipo de documento no es válido",
                        "El número de documento no es válido",
                        "Lo sentimos, la pagina del Sisben no responde en este momento. Por favor, intenta de nuevo mas tarde."
                    ]
                }
            }
        ), 
    }
)
@api_view(['GET', 'POST'])
@permission_classes([APIKeyPermission])
def validate_sisben(request: Request):
    try:
        docType = request.query_params.get('docType')
        numDoc = request.query_params.get('numDoc')

        session = SisbenSession()

        validateParams(docType, numDoc, session.get_types_document())

        data = session.get_sisben(docType, numDoc)

        municipio = data['persona']['municipio']
        departamento = data['persona']['departamento']

        if municipio.lower() == 'Villa del Rosario'.lower() and departamento.lower() == 'Norte de Santander'.lower():
            session.reset_session()
            return Response({'mensaje': f'Existe'}, status=200, content_type='application/json')
        
        session.reset_session()
        return Response({
            'mensaje': f'Existe, pero no en Villa del Rosario'
        }, status=200, content_type='application/json')
    except ValueError as ve:
        session.close_session()
        return Response({'mensaje': 'No existe en el sisben.' }, status=200, content_type='application/json')
    except Exception as e:
        session.close_session()
        return Response({'mensaje': str(e)}, status=200, content_type='application/json')

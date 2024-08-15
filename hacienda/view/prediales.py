from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from hacienda.helpers.tnsrequest import TNSRequest
from hacienda.utils.transformres import formatmessage, formatpredial, convertBase64ToPDF
from hacienda.utils.shorturl import shorturl
from hacienda.models import PredialSearch, ESTADOS, PredialUrlShort
from datetime import timedelta
from shared.auth.apikey import APIKeyPermission
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os

tns = TNSRequest()

@swagger_auto_schema(
    tags=['Hacienda'],
    methods=('get', 'post'),
    operation_description="Obtiene los prediales de una persona por su número de documento",
    manual_parameters=[
        openapi.Parameter(
            'documento', 
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
                    "mensaje":'1) K5 xxx xxx xxx'
                }
            },
        ), 
        400: openapi.Response
        (
            description="Se envia un mensaje de error dependiendo de lo que salga mal en la consulta", 
            examples={
                "application/json": {
                    "mensaje": [
                        "El número de documento es requerido."
                        'Ha ocurrido un error. Intenta de nuevo más tarde.',
                        'No se encontraron predios para el documento xxxxxxxxx.',
                        'Estamos teniendo problemas con el servicio, por favor intente más tarde.'
                    ]
                }
            }
        ), 
    }
)
@api_view(['GET', 'POST'])
@permission_classes([APIKeyPermission])
def getprediales(request: Request):
    try:
        numDoc = request.query_params.get('documento')

        if numDoc is None:
            return Response({'mensaje': 'El número de documento es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Elimina cualquier registro que haya tenido antes el usuario
        predialobj = PredialSearch.objects.filter(cedula=numDoc).first()

        if predialobj is not None:
            predialobj.delete()

        prediales = tns.getprediales(numDoc)
        finalmessage = f'{formatmessage(prediales=prediales)}'

        # se guarda momentaneamente la consulta en la base de datos 
        PredialSearch.objects.create(
            cedula=numDoc,
            prediales=formatpredial(prediales=prediales),
            estado=ESTADOS['CONSULTA_PREDIAL_GENERAL'],
            primera_consulta=timezone.now() - timedelta(hours=5),
            mensaje = 'mensaje'
        ).save()

        return Response({'mensaje': finalmessage }, status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response({'mensaje': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'mensaje': 'Ha ocurrido un error. Intenta de nuevo más tarde.'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    tags=['Hacienda'],
    methods=('get', 'post'),
    operation_description="Obtiene la url de acceso al pdf del predial consultado.",
    manual_parameters=[
        openapi.Parameter(
            'documento', 
            openapi.IN_QUERY, 
            description="Número de documento de la persona", 
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'opcion', 
            openapi.IN_QUERY, 
            description="Número de la opción de predial que desea consultar", 
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
                    "mensaje": 'http://localhost:8000/media/predial-xxxxxxx.pdf' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}/media/predial-xxxxxxx.pdf'
                }
            },
        ), 
        400: openapi.Response
        (
            description="Se envia un mensaje de error dependiendo de lo que salga mal en la consulta", 
            examples={
                "application/json": {
                    "mensaje": [
                        "El número de documento es requerido."
                        'Parece ser que no haz consultado con anterioridad los prediales. Te invitamos a que lo hagas.',
                        'La opcion no es correcta. Ingresa una de las opciones indicadas anteriormente.'
                        'Estamos teniendo problemas con el servicio, por favor intente más tarde.',
                        'Ha ocurrido un error. Intenta de nuevo más tarde.',
                    ]
                }
            }
        ), 
    }
)
@api_view(['GET', 'POST'])
@permission_classes([APIKeyPermission])
def getpredialpdf(request: Request):
    try:

        numDoc = request.query_params.get('documento')
        predialOption = request.query_params.get('opcion')

        if numDoc is None:
            return Response({'mensaje': 'El número de documento es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Comprobamos que el usuario ya haya consultado los prediales anteriormente 
        predialObj = PredialSearch.objects.filter(cedula=numDoc).first()

        if predialObj is None:
            return Response({'mensaje': 'Parece ser que no haz consultado con anterioridad los prediales. Te invitamos a que lo hagas.'}, status=status.HTTP_400_BAD_REQUEST)
        
        prediales = predialObj.prediales.split(' ')

        if predialOption is None or not predialOption.isnumeric():
            return Response({'mensaje': 'La opcion no es correcta. Ingresa una de las opciones indicadas anteriormente.'}, status=status.HTTP_400_BAD_REQUEST)

        predialOption = int(predialOption)
        
        # se valida que el usuario ingrese una opcion valida dependiendo de la cantidad de prediales que tenga. 
        if not (1 <= int(predialOption) < len(prediales)):
            return Response({'mensaje': 'La opcion no es correcta. Ingresa una de las opciones indicadas anteriormente.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # se obtiene el pdf y el link de pago
        response = tns.getpaymethod(prediales[predialOption-1])
        print(response)
        # Crear el nombre del archivo y definir su ruta de acceso
        filename = f'predial-{prediales[predialOption-1]}.pdf'
        path = os.path.join(settings.MEDIA_ROOT, f'{filename}')

        convertBase64ToPDF(response[0], path)
        shortUrl = shorturl(url=response[1])

        predialObj.estado = ESTADOS['CONSULTA_PREDIAL_OBJETIVO']
        predialObj.link_cobro = shortUrl[1]
        predialObj.nombre_archivo = filename
        predialObj.save()

        
        # save the url shor link
        PredialUrlShort.objects.create(
            original_url = shortUrl[2],
            short_id = shortUrl[0]
        ).save()

        accessLink = f'http://localhost:8000/media/{filename}' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}/media/{filename}'

        return Response({'mensaje' : accessLink}, status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response({'mensaje': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    tags=['Hacienda'],
    methods=('get', 'post'),
    operation_description="Obtiene el link de pago del predial consultado.",
    manual_parameters=[
        openapi.Parameter(
            'documento', 
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
                    "mensaje": 'http://localhost:8000/tns-predial-pago-online/7882x8' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}/tns-predial-pago-online/7882x8'
                }
            },
        ), 
        400: openapi.Response
        (
            description="Se envia un mensaje de error dependiendo de lo que salga mal en la consulta", 
            examples={
                "application/json": {
                    "mensaje": [
                        "El número de documento es requerido."
                        'Parece ser que no haz consultado con anterioridad los prediales. Te invitamos a que lo hagas.',
                        'Estamos teniendo problemas con el servicio, por favor intente más tarde.',
                        'Ha ocurrido un error. Intenta de nuevo más tarde.',
                    ]
                }
            }
        ), 
    }
)
@api_view(['GET', 'POST'])
@permission_classes([APIKeyPermission])
def getpaymethod(request: Request):
    try:
        numDoc = request.query_params.get('documento')
        
        if numDoc is None:
            return Response({'mensaje': 'El número de documento es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        predialObj = PredialSearch.objects.filter(cedula=numDoc).first()

        if predialObj is None:
            return Response({'mensaje': 'Parece ser que no haz consultado con anterioridad los prediales. Te invitamos a que lo hagas.'}, status=status.HTTP_400_BAD_REQUEST)
        
        link_cobro = f'{predialObj.link_cobro}'
        
        return Response({'mensaje': link_cobro}, status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response({'mensaje': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=['get', 'post'],
    auto_schema=None
)
@api_view(['GET', 'POST'])
def redirectToOriginalLink(request: Request, short_id: str):
    try:
       urlObj = get_object_or_404(PredialUrlShort, short_id=short_id)
       return redirect(urlObj.original_url)
    except Exception as e:
        return Response({'mensaje': 'El link al que intenta acceder no se encuentra disponible.'}, status=status.HTTP_404_NOT_FOUND)


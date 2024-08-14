from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from hacienda.helpers.tnsrequest import TNSRequest
from hacienda.utils.icatransform import getmessage, gethistorialmessage
from shared.auth.apikey import APIKeyPermission
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

tns = TNSRequest()

@swagger_auto_schema(
    tags=['Hacienda'],
    methods=('get', 'post'),
    operation_description="Obtiene los locales de una persona por su número de documento",
    manual_parameters=[
        openapi.Parameter(
            'cc', 
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
                    "mensaje":'1) <#placa> - <Nombre local comercial> ...'
                }
            },
        ), 
        400: openapi.Response
        (
            description="Se envia un mensaje de error dependiendo de lo que salga mal en la consulta", 
            examples={
                "application/json": {
                    "mensaje": [
                        "El número de documento es requerido para realizar la consulta."
                        'Ha ocurrido un error. Intenta de nuevo más tarde.',
                        'Estamos teniendo problemas con el servicio, por favor intente más tarde.'
                    ]
                }
            }
        ), 
    }
)
@api_view(['GET', 'POST'])
@permission_classes([APIKeyPermission])
def getlocalesbycc(request: Request):
    try:
        cc = request.query_params.get('cc')

        if cc is None:
            return Response({'mensaje': 'El número de documento es requerido para realizar la consulta.'}, status=status.HTTP_400_BAD_REQUEST)
        
        tnsresponse = tns.getlocalesbycc(cc=cc)

        message = getmessage(establecimientos=tnsresponse)
        return Response({'mensaje': message}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    tags=['Hacienda'],
    methods=('get', 'post'),
    operation_description="Obtiene el historial de pago del local mediante su número de placa",
    manual_parameters=[
        openapi.Parameter(
            'placa', 
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
                    "mensaje":' Lista detallada de los pagos realizados.'
                }
            },
        ), 
        400: openapi.Response
        (
            description="Se envia un mensaje de error dependiendo de lo que salga mal en la consulta", 
            examples={
                "application/json": {
                    "mensaje": [
                        "La placa es requerida para realizar la consulta.",
                        "La placa debe ser un número.",
                        'Ha ocurrido un error. Intenta de nuevo más tarde.',
                        'Estamos teniendo problemas con el servicio, por favor intente más tarde.'
                    ]
                }
            }
        ), 
    }
)
@api_view(['GET', 'POST'])
@permission_classes([APIKeyPermission])
def gethistorialbyplaca(request:Request):
    try:
        placa = request.query_params.get('placa')

        if placa is None:
            return Response({'mensaje': 'La placa es requerida para realizar la consulta.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not placa.isnumeric():
            return Response({'mensaje': 'La placa debe ser un número.'}, status=status.HTTP_400_BAD_REQUEST)
        
        tnsresponse = tns.gethistorybyplaca(placa=placa)

        message = gethistorialmessage(historial=tnsresponse)
        return Response({'mensaje': message}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)
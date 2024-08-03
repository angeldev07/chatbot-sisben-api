from django.utils import timezone
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from hacienda.helpers.tnsrequest import TNSRequest
from hacienda.utils.transformres import formatmessage, formatpredial, convertBase64ToPDF
from hacienda.models import PredialSearch, ESTADOS
from datetime import timedelta
import os

tns = TNSRequest()

@api_view(['GET', 'POST'])
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
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'POST'])
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

        # Crear el nombre del archivo y definir su ruta de acceso
        filename = f'predial-{prediales[predialOption-1]}.pdf'
        path = os.path.join(settings.MEDIA_ROOT, f'{filename}')

        convertBase64ToPDF(response[0], path)

        predialObj.estado = ESTADOS['CONSULTA_PREDIAL_OBJETIVO']
        predialObj.link_cobro = response[1]
        predialObj.nombre_archivo = filename
        predialObj.save()

        accessLink = f'http://localhost:8000/media/{filename}' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}/media/{filename}'

        return Response({'mensaje' : accessLink}, status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response({'mensaje': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'POST'])
def getpaymethod(request: Request):
    try:
        numDoc = request.query_params.get('documento')
        
        if numDoc is None:
            return Response({'mensaje': 'El número de documento es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        predialObj = PredialSearch.objects.filter(cedula=numDoc).first()

        if predialObj is None:
            return Response({'mensaje': 'Parece ser que no haz consultado con anterioridad los prediales. Te invitamos a que lo hagas.'}, status=status.HTTP_400_BAD_REQUEST)
        
        link_cobro = f'👨‍💻 En el siguiente enlace podras realizar el pago del predial solicitado. DY_SALTO {predialObj.link_cobro}'
        
        return Response({'mensaje': link_cobro}, status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response({'mensaje': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

# ================================================================================================  Metodos directos =======================================================================================

@api_view(['GET', 'POST'])
def getpredialdirect(request: Request):
    try:
        
        numDoc = request.query_params.get('documento')

        if numDoc is None:
            return Response({'mensaje': 'El número de documento es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        prediales = tns.getprediales(numDoc)
        finalmessage = f'He encontrado estos predios relacionados al N° documento: *{numDoc}*. Por favor, envíame el número del predio que quieres liquidar:\n {formatmessage(prediales=prediales)}'

        return Response({'mensaje': finalmessage}, status=status.HTTP_200_OK)


    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'POST'])
def getpredialpdfdirect(request: Request):
    try:

        predial = request.query_params.get('predial')

        if predial is None:
            return Response({'mensaje': 'El número de predial es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        response = tns.getpaymethod(predial)

        path = os.path.join(settings.MEDIA_ROOT, f'predial-{predial}.pdf')

        convertBase64ToPDF(response[0], path)
        accessLink = f'http://localhost:8000/media/predial-{predial}.pdf' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}/media/predial-{predial}.pdf'

        return Response({'mensaje' : accessLink}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'POST'])
def getpaymethoddirect(request: Request):
    try:
        predial = request.query_params.get('predial')
        if predial is None:
            return Response({'mensaje': 'El número de predial es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        response = tns.getpaymethod(predial)

        # comprobar si el archivo existe
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, f'predial-{predial}.pdf')):
            os.remove(os.path.join(settings.MEDIA_ROOT, f'predial-{predial}.pdf'))


        return Response({'mensaje': response[1]}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)
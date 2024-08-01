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
            return Response({'error': 'El número de documento es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Elimina cualquier registro que haya tenido antes el usuario
        predialobj = PredialSearch.objects.filter(cedula=numDoc).first()
        if predialobj is not None:
            lasttime = (timezone.now() - timedelta(hours=5)) - predialobj.primera_consulta
            if lasttime > timedelta(hours=1):
                predialobj.delete()
            else:
                return Response({'mensaje': predialobj.mensaje}, status=status.HTTP_200_OK)

        
        prediales = tns.getprediales(numDoc)
        finalmessage = f'He encontrado estos predios relacionados al N° documento: *{numDoc}*. Por favor, envíame el número del predio que quieres liquidar:\n {formatmessage(prediales=prediales)}'

        PredialSearch.objects.create(
            cedula=numDoc,
            prediales=formatpredial(prediales=prediales),
            estado=ESTADOS['CONSULTA_PREDIAL_GENERAL'],
            primera_consulta=timezone.now() - timedelta(hours=5),
            mensaje = finalmessage
        ).save()

        return Response({'mensaje': finalmessage}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET', 'POST'])
def getpredialpdf(request: Request):
    try:

        numDoc = request.query_params.get('documento')
        predialOption = int(request.query_params.get('opcion'))

        if numDoc is None:
            return Response({'error': 'El número de documento es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        predialObj = PredialSearch.objects.filter(cedula=numDoc).first()

        if predialObj is None:
            return Response({'mensaje': 'Parece ser que no haz consultado con anterioridad los prediales. Te invitamos a que lo hagas.'}, status=status.HTTP_400_BAD_REQUEST)
        
        prediales = predialObj.prediales.split(' ')

        if not (1 <= predialOption <= len(prediales)):
            return Response({'mensaje': 'La opcion no es correcta. Ingresa una de las opciones indicadas anteriormente.'}, status=status.HTTP_400_BAD_REQUEST)
        
        response = tns.getpaymethod(prediales[predialOption-1])
        path = os.path.join(settings.MEDIA_ROOT, f'{numDoc}-{prediales[predialOption-1]}.pdf')

        convertPdf = convertBase64ToPDF(response[0], path)

        predialObj.estado = ESTADOS['CONSULTA_PREDIAL_OBJETIVO']
        predialObj.link_cobro = response[1]
        predialObj.save()

        accessLink = f'http://localhost:8000/media/{numDoc}-{prediales[predialOption-1]}.pdf' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}/media/{numDoc}-{prediales[predialOption-1]}.pdf'

        return Response({'mensaje' : accessLink}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET', 'POST'])
def getpaymethod(request: Request):
    try:
        numDoc = request.query_params.get('documento')
        if numDoc is None:
            return Response({'error': 'El número de documento es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        predialObj = PredialSearch.objects.filter(cedula=numDoc).first()

        if predialObj is None:
            return Response({'mensaje': 'Parece ser que no haz consultado con anterioridad los prediales. Te invitamos a que lo hagas.'}, status=status.HTTP_400_BAD_REQUEST)
        
        link_cobro = predialObj.link_cobro

        predialObj.delete()
        
        return Response({'mensaje': link_cobro}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
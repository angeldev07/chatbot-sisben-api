from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from sisben.helpers.session import SisbenSession
from sisben.utils.get_sisben_fns import validateParams, generar_pdf
import os 

session = SisbenSession()

@api_view(['GET', 'POST'])
def sisben(request: Request):
    try:
        # Obtiene el tipo de documento y el número de documento de la consulta
        docType = request.query_params.get('docType')
        numDoc = request.query_params.get('numDoc')

        # Valida los parámetros de entrada
        validateParams(docType, numDoc, session)

        data = session.get_sisben(docType, numDoc)
        
        context = {
            'persona': data['persona'],
            'sisben': data['sisben'],
        }

        # Genera el PDF de la consulta del Sisben
        download_url = generar_pdf(request, context, numDoc)

        #Obtiene la url de acceso al pdf. 
        data['download_url'] = f'http://localhost:8000{download_url}' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}{download_url}'

        return Response({ 'mensaje': f'👉 {data['download_url']}' } , status=200, content_type='application/json')
    except ValueError as ve:
        return Response({'mensaje': str(ve)}, status=200, content_type='application/json')
    except Exception as e:
        return Response( { 'mensaje': str(e) }, status=200, content_type='application/json')
    

@api_view(['GET', 'POST'])
def validate_sisben(request: Request):
    try:
        docType = request.query_params.get('docType')
        numDoc = request.query_params.get('numDoc')

        validateParams(docType, numDoc, session)

        data = session.get_sisben(docType, numDoc)

        municipio = data['persona']['municipio']
        departamento = data['persona']['departamento']

        if municipio.lower() == 'Villa del Rosario'.lower() and departamento.lower() == 'Norte de Santander'.lower():
            return Response({'mensaje': f'Hemos comprobado que cuenta con su sisben en {departamento} - {municipio}'}, status=200, content_type='application/json')

        return Response({
            'mensaje': f'Hemos detectado que tiene su sisben registrado en {departamento}-{municipio}. Lo invitamos a que se acerque a la oficina del sisben del lugar indicado para realizar su solicitud.'
        }, status=200, content_type='application/json')
    except ValueError as ve:
        return Response({'mensaje': str(ve) }, status=200, content_type='application/json')
    except Exception as e:
        return Response({'mensaje': str(e)}, status=200, content_type='application/json')


@api_view(['GET', 'POST'])
def get_message(request: Request):
    return Response({'mensaje': 'Hola mundo'}, status=200, content_type='application/json')
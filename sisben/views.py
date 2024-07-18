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
    # Obtiene el tipo de documento y el número de documento de la consulta
    docType = request.query_params.get('docType')
    numDoc = request.query_params.get('numDoc')
    try:
        # Valida los parámetros de entrada
        validateParams(docType, numDoc, session)

        data = session.get_sisben(docType, numDoc)

        if data['status_code'] != 200:
            return Response(data, status=200, content_type='text/plain')
        
        context = {
            'persona': data['persona'],
            'sisben': data['sisben'],
        }

        # Genera el PDF de la consulta del Sisben
        download_url = generar_pdf(request, context, numDoc)

        if settings.DEBUG:
            return Response(f'http://localhost:8000{download_url}', status=200, content_type='text/plain')

        return Response(f'{os.environ.get('IP_SERVER')}{download_url}', status=200, content_type='text/plain')
    except ValueError as ve:
        return Response(str(ve), status=200, content_type='text/plain')
    except Exception as e:
        return Response(str(e), status=200, content_type='text/plain')

@api_view(['GET', 'POST'])
def get_message(request: Request):
    return Response('Hola mundo!!!', status=200, content_type='text/plain')
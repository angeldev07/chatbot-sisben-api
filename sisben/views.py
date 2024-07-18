from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from sisben.helpers.session import SisbenSession
from sisben.utils.get_sisben_fns import validateParams, generar_pdf
from sisben.helpers.logs import write_log
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
            write_log(str(data), data['status_code'], request.build_absolute_uri())
            return Response(data, status=200, content_type='text/plain')
        
        context = {
            'persona': data['persona'],
            'sisben': data['sisben'],
        }

        # Genera el PDF de la consulta del Sisben
        download_url = generar_pdf(request, context, numDoc)

        if settings.DEBUG:
            write_log(f'http://localhost:8000{download_url}', 200, request.build_absolute_uri())
            return Response(f'http://localhost:8000{download_url}', status=200, content_type='text/plain')

        write_log(f'{os.environ.get('IP_SERVER')}{download_url}', 200, request.build_absolute_uri())
        return Response(f'{os.environ.get('IP_SERVER')}{download_url}', status=200, content_type='text/plain')
    except ValueError as ve:
        write_log(str(ve), 400, request.build_absolute_uri())
        return Response(str(ve), status=200, content_type='text/plain')
    except Exception as e:
        write_log(str(e), 500, request.build_absolute_uri())
        return Response(str(e), status=200, content_type='text/plain')

@api_view(['GET', 'POST'])
def get_message(request: Request):
    write_log('Hola mundo!!!', 200, request.build_absolute_uri())
    return Response('Hola mundo!!!', status=200, content_type='text/plain')
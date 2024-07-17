from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from weasyprint import HTML
from sisben.helpers.session import SisbenSession
from sisben.utils.get_sisben_fns import validateParams, generar_pdf
import os 

session = SisbenSession()

@api_view(['GET'])
def sisben(request: Request):
    # Obtiene el tipo de documento y el número de documento de la consulta
    docType = request.query_params.get('docType')
    numDoc = request.query_params.get('numDoc')
    try:
        # Valida los parámetros de entrada
        validateParams(docType, numDoc, session)

        data = session.get_sisben(docType, numDoc)

        if data['status_code'] != 200:
            return Response(data, status=data['status_code'])
        
        context = {
            'persona': data['persona'],
            'sisben': data['sisben'],
        }

        # Genera el PDF de la consulta del Sisben
        download_url = generar_pdf(request, context, numDoc)

        if settings.DEBUG:
            return Response(f'http://localhost:8000{download_url}', status=200)

        return Response(f'{os.environ.get('IP_SERVER')}{download_url}', status=200)
    except ValueError as ve:
        return Response(str(ve), status=400)
    except Exception as e:
        e.with_traceback()
        return Response(str(e), status=500)

@api_view(['GET'])
def get_message(request: Request):
    return Response('Hola mundo!!!', status=200)
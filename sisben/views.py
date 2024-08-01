from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from sisben.helpers.session import SisbenSession
from sisben.utils.get_sisben_fns import validateParams, generar_pdf
import os 


@api_view(['GET', 'POST'])
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
    

@api_view(['GET', 'POST'])
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


@api_view(['GET', 'POST'])
def get_message(request: Request):
    return Response({'mensaje': 'Hola mundo'}, status=200, content_type='application/json')
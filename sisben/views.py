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
            return Response(data, status=200, content_type='application/json')
        
        context = {
            'persona': data['persona'],
            'sisben': data['sisben'],
        }

        # Genera el PDF de la consulta del Sisben
        download_url = generar_pdf(request, context, numDoc)

        #Obtiene la url de acceso al pdf. 
        data['download_url'] = f'http://localhost:8000{download_url}' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}{download_url}'

        # escribe el log de lo que se retorna
        write_log( {'mensaje': f'Su pdf se encuentra en 👉 {data['download_url']}' }, 200, request.build_absolute_uri())

        return Response({ 'mensaje': f'Su pdf se encuentra en 👉 {data['download_url']}' } , status=200, content_type='application/json')
    except ValueError as ve:
        write_log({'mensaje': str(ve)}, 400, request.build_absolute_uri())
        return Response({'mensaje': str(ve)}, status=200, content_type='application/json')
    except Exception as e:
        write_log( { 'mensaje': str(e) }, 500, request.build_absolute_uri())
        return Response( { 'mensaje': str(e) }, status=200, content_type='application/json')
    

@api_view(['GET', 'POST'])
def validate_sisben(request: Request):
    docType = request.query_params.get('docType')
    numDoc = request.query_params.get('numDoc')
    try:
        validateParams(docType, numDoc, session)

        data = session.get_sisben(docType, numDoc)

        municipio = data['persona']['municipio']
        departamento = data['persona']['departamento']

        if municipio.lower() == 'Villa del Rosario'.lower() and departamento.lower() == 'Norte de Santander'.lower():
            write_log({'mensaje': 'existe'}, 200, request.build_absolute_uri())
            return Response({'mensaje': f'Hemos comprobado que cuenta con su sisben en {departamento} - {municipio}'}, status=200, content_type='application/json')

        write_log({
            'mensaje': f'Hemos detectado que tiene su sisben registrado en {departamento}-{municipio}. Lo invitamos a que se acerque a la oficina del sisben del lugar indicado para realizar su solicitud.'
        }, 200, request.build_absolute_uri())
        
        return Response({
            'mensaje': f'Hemos detectado que tiene su sisben registrado en {departamento}-{municipio}. Lo invitamos a que se acerque a la oficina del sisben del lugar indicado para realizar su solicitud.'
        }, status=200, content_type='application/json')
    except ValueError as ve:
        write_log({'mensaje': str(ve) }, 400, request.build_absolute_uri())
        return Response({'mensaje': str(ve) }, status=200, content_type='application/json')
    except Exception as e:
        write_log({'mensaje': str(e)}, 500, request.build_absolute_uri())
        return Response({'mensaje': str(e)}, status=200, content_type='application/json')


@api_view(['GET', 'POST'])
def get_message(request: Request):
    write_log('Hola mundo!!!', 200, request.build_absolute_uri())
    return Response({'mensaje': 'Hola mundo'}, status=200, content_type='application/json')
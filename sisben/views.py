from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from weasyprint import HTML
from sisben.helpers.session import SisbenSession
import os 

session = SisbenSession()

@api_view(['GET'])
def sisben(request: Request):
    # Obtiene el tipo de documento y el número de documento de la consulta
    type = request.query_params.get('t')
    id = request.query_params.get('id')
    try:
        data = session.get_sisben(type, id)

        if data['status_code'] != 200:
            return Response(data, status=data['status_code'])
        
        context = {
            'persona': data['persona'],
            'sisben': data['sisben'],
        }

        html_string = render_to_string('sisben.html', context)

        # Genera el PDF usando WeasyPrint
        pdf_file = HTML(string=html_string).write_pdf()

        # Guarda el PDF en el directorio 'media' de tu proyecto
        file_path = os.path.join(settings.MEDIA_ROOT, f'{id}.pdf')
        with open(file_path, 'wb') as f:
            f.write(pdf_file)

        # Retorna la URL del archivo para descargar
        download_url = settings.MEDIA_URL + f'{id}.pdf'

        context['download_url'] = download_url
        return Response(context, status=200)
    except Exception as e:
        e.with_traceback()
        return Response(data={'error': str(e)}, status=500)

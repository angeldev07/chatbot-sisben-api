from django.template.loader import get_template
from django.conf import settings
from weasyprint import HTML
import re
import os


def validateDoc(numDoc):
    """Valida el número de documento de la persona a consultar el sisben.

    Args:
        numDoc (str | number): Número de documento de la persona a consultar el sisben.

    Returns:
        bool: True si el número de documento es válido, False en caso contrario.
    """
    pattern = re.compile(r'^\d{6,10}$')
    return pattern.match(str(numDoc)) is not None

def validateParams(docType, numDoc, typesDocs):
    """
        Valida los parámetros de entrada para la vista sisben.

    Args:
        docType (number): Tipo de documento, debe estar comprendido entre 1 y 9
        numDoc (text | number): Número de documento de la persona a consultar el sisben.
        session (SisbenSession): Objeto de la clase SisbenSession que hace referencia a la sesión activa.

    Raises:
        ValueError: Lo sentimos, el tipo de documento es requerido -> Si docType es None
        ValueError: Lo sentimos, el número de documento es requerido -> Si numDoc es None
        ValueError: Lo sentimos, el tipo de documento no es válido -> Si docType no está en los tipos de documento válidos
    """
    if docType is None:
        raise ValueError('Lo sentimos, el tipo de documento es requerido')
    if not validateDoc(numDoc) :
        raise ValueError('Lo sentimos, el número de documento no es válido')
    if numDoc is None:
        raise ValueError('Lo sentimos, el número de documento es requerido')
    if docType not in typesDocs.keys():
        raise ValueError('Lo sentimos, el tipo de documento no es válido')


def generar_pdf(request, context, numDoc):
    """
        Genera el PDF de la consulta del Sisben.
    Args:
        context (Dict): Diccionario con la información de la consulta del Sisben. Debe ser un diccionario con las siguientes llaves:
                        - persona: Diccionario con la información de la persona consultada. Debe tener las siguientes llaves:
                            - nombres (str): Nombres de la persona.
                            - apellidos (str): Apellidos de la persona.
                            - tipo_documento (str): Tipo de documento de la persona.
                            - numero_documento (str): Número de documento de la persona.
                            - municipio (str): Municipio donde tiene registrado el sisben la persona.
                            - departamento (str): Departamento donde tiene registrado el sisben la persona.
                        - sisben: Diccionario con la información del Sisben. Debe tener las siguientes llaves:
                            - fecha_consulta (str): Fecha de la consulta del Sisben.
                            - ficha (str): Ficha de registro del Sisben.
                            - puntaje (str): Puntaje del Sisben.
                            - nivel_pobreza (str): Nivel de pobreza acorde al puntaje del Sisben.
                        -status_code (number): Código de estado de la consulta del Sisben.

        numDoc (text | number): Número de documento de la persona a consultar el sisben.

    Returns:
        str: URL del archivo PDF generado.
    """
    template = get_template('sisben.html')
    html = template.render(context)

    pdf = HTML(string=html, base_url=request.build_absolute_uri(), ).write_pdf(
        presentational_hints=True,
    )
    file_path = os.path.join(settings.MEDIA_ROOT, f'{numDoc}.pdf')
    with open(file_path, 'wb') as f:
        f.write(pdf)
    return settings.MEDIA_URL + f'{numDoc}.pdf'
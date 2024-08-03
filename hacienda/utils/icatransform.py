from shared.utils.getmonth import getMonth
import locale

def getmessage(establecimientos: list) -> str:
    """Obtiene el mensaje final para enviar al chatbot

    Args:
        establecimientos (list): Lista de establecimientos obtenidos en la API de TNS

    Returns:
        str: Mensaje final para enviar al chatbot ejemplo
        *OCODIGO* - ONOMBRE
        *OCODIGO* - ONOMBRE

        si tiene mas de un establecimiento. 
    """
    message = ''
    # establecimiento['ONOMBRE']
    for establecimiento in establecimientos:
        message += f"*Placa*: *{establecimiento['OCODIGO']}* DY_SALTO*Local*:{establecimiento['ONOMBRE']} DY_SALTO"
    return message

def gethistorialmessage(historial: list) -> str:
    message = ''
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
    for history in historial:
        pagado_format = locale.currency(float(history['OTOTALPAGO']), grouping=True)
        message += f'*Periodo*: {getMonth(int(history['OPERIODO']))} DY_SALTO*Fecha*: {history['OFECHA']} DY_SALTO*Pagado*: {pagado_format} DY_SALTO'
    return message
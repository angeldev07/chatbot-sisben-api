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
    for establecimiento in establecimientos:
        message += f"*{establecimiento['OCODIGO']}* - {establecimiento['ONOMBRE']}                                                                                                                            \n" #no borrar los espacios exagerados, el \n es por si cuela xd
    return message
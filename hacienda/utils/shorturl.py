"""
    Development by Angel Garcia 
    CopyRight 2024 by Emsitel S.A.S
"""

def shorturl(url: str, serverEndpoint = 'tns-predial-pago-online'):
    """Genera un identificador unico para cada url de pago de TNS que se envia.

    Args:
        url (str): Url original de pago generado por TNS
        serverEndpoint (str, optional): Endpoint desde el cual se va a servir la direccion. Defaults to 'tns-predial-pago-online'.

    Returns:
        tuple: Una tupla con los siguientes elementos:
                0: Identificador unico de la url
                1: Url convertida
                2: Url original
    """
    import hashlib
    import os
    from django.conf import settings
    # in this case, the server has the domain name (https://alcaldiavilla.emsitel.co)
    server  = os.environ.get('IP_SERVER')
    # hash the url and take the first 7 characters
    hashed_url = hashlib.md5(url.encode()).hexdigest()[:7]
    finalurl = f'http://localhost:8000/{serverEndpoint}/{hashed_url}' if settings.DEBUG else f'{server}/{serverEndpoint}/{hashed_url}'
    return (hashed_url, finalurl, url)

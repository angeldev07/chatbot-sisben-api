import requests
from requests.models import Response
import os 
from dotenv import load_dotenv

load_dotenv()

class TNSRequest:
    def __init__(self):
        """
            Inicializa la instancia de TNSRequest con la URL base y los endpoints disponibles.
        """
        self.url = "https://api-gov.tns.co/api/"
        self.endpoints = {
            'prediales': {
                'listar': 'Predial/ListarPrediosDocumento',
                'pdf': 'Predial/GenRecTemporalFicha',
            },
            'ica': {
                'establecimientos': 'Local/ListarEstablecimientosDocumento',
                'historial': 'Local/GetAllDeclaracionesPlaca',
            }
        }
        self.request = requests

    def __env(self):
        """
            Obtiene las variables de entorno necesarias para la autenticación en el API.

            Returns:
                dict: Un diccionario con las variables de entorno de autenticación.
        """
        return {
            'empresa': os.environ.get('CODIGO_EMPRESA'),
            'usuario': os.environ.get('USUARIO'),
            'password': os.environ.get('PASSWD'),
            'tnsapitoken': os.environ.get('TNSTOKEN'),
        }
    
    def geturlrequest(self,queryparams: dict):
        """Obtiene la url final para hacer la peticion a la api de tns

        Args:
            queryparams (dict): Los query params que necesita la API. No se deben de incluir los requeridos por tns como empresa, usuario, password y tnsapitoken.

        Returns:
            str: La url completa para hacer la petición
        """
        envs = self.__env()
        for key, value in queryparams.items():
            extra = f'&{key}={value}'
        return f'empresa={envs['empresa']}&usuario={envs['usuario']}&password={envs['password']}&tnsapitoken={envs['tnsapitoken']}&{extra}'
    
    def validate_response(self, response: Response, api_err_message: str, custom_err_message:str):
        """Valida que la respuesta del api sea exitosa

        Args:
            response (Response): respuesta de la api de tns
            api_err_message (str): Trozo del mensaje de error qeu retorna la api de tns 
            custom_err_message (str): Mensaje personalizado de error en caso del que en la api de tns no sea claro.

        Raises:
            ValueError: Mensaje de error personalizado en caso de que se envie
            ValueError: Estamos teniendo problemas con el servicio, por favor intente más tarde.

        Returns:
            json: Respuesta parseada a json si es exitosa. 
        """
        if response.status_code >= 400 and response.status_code < 600:
            error = response.json()
            if api_err_message and ( api_err_message.lower() in error['results'].lower() ):
                raise ValueError(custom_err_message)
            raise ValueError('Estamos teniendo problemas con el servicio, por favor intente más tarde.' if not custom_err_message else custom_err_message)
        return response.json()
        
    def make_request(self, endpoint: str, queryparams: dict, method: str, api_err_message: str = None, custom_err_message:str = None):
        """
            Realiza la petición a la API de tns
        Args:
            endpoint (str): endpoint a hacer la peticion. Se encuentra en la propiedad endpoints
            queryparams (dict): queryparams necesarios para hacer la peticion. Solo agregar los que son cambiantes, ya se tiene en cuenta los requeridos por tns.
            method (str): metodo http a realizar
            api_err_message (str): Un trozo del mensaje de error que retorna la api de tns en caso de querer enviar mensajes personalizados
            custom_err_message (str): Mensaje de error personalizado.

        Raises:
            ValueError: Mensaje de error personalizado en caso de que se envie. 

        Returns:
            json: Retorna un json de la peticion en caso de que se responda con status 200.
        """
        try:
            request = self.geturlrequest(queryparams)

            if method.lower() == 'GET'.lower():
                response = self.request.get(f'{self.url}{endpoint}?{request}')
            elif method.lower() == 'POST'.lower():
                response = self.request.post(f'{self.url}{endpoint}?{request}')
            else:
                raise ValueError('Método no permitido.')
            
            return self.validate_response(
                response=response,
                api_err_message=api_err_message,
                custom_err_message=custom_err_message,
            )
        except Exception as e:
            raise

    def getprediales(self, cc):
        """
            Consulta la lista de predios asociados a un documento específico.

            Args:
                cc (str): El documento de identidad para buscar los predios.

            Returns:
                dict: La respuesta del API con la lista de predios.

            Raises:
                ValueError: Si no se encontraron predios o hay un problema con el servicio.
        """       
        try:
            return self.make_request(
                method='get',
                queryparams= {
                    'documento': cc
                },
                endpoint=self.endpoints["prediales"]['listar'],
                api_err_message='No se encontraron predios',
                custom_err_message=f'No se han encontrado predios relacionados para el documento {cc}'
            )
        except Exception as e:
            raise

    def getpaymethod(self, ficha):
        """
            Obtiene el método de pago asociado a una ficha específica.

            Args:
                ficha (str): La ficha para generar el reporte de pago.

            Returns:
                dict: La respuesta del API con el método de pago.

            Raises:
                ValueError: Si hay un problema con el servicio.
        """
        try:
            return self.make_request(
                method='post',
                queryparams={
                    'ficha': ficha
                },
                endpoint=self.endpoints["prediales"]["pdf"],
            )
        except Exception as e:
            raise

    def getlocalesbycc(self, cc):
        """
        Args:
            cc (str): Número de la cédula.

        Raises:
            ValueError: No se encontro el establecimiento para el documento _documento_. 
            ValueError: Estamos teniendo problemas con el servicio, por favor intente más tarde.

        Returns:
           dict: Respuesta de la API de TNS, los campos son:
                  - OCODIGO: Código del establecimiento.
                  - ONOMBRE: Nombre del establecimiento.
                  - ODIRECCION: Dirección del establecimiento.
        """
        try:
            return self.make_request(
                method='get',
                queryparams={
                    'documento': cc
                },
                endpoint=self.endpoints['ica']['establecimientos'],
                api_err_message='No se encontro el establecimiento',
                custom_err_message=f'No se han encontrado establecimientos comerciales asociados al documenot *{cc}*'
            )
        except Exception as e:
            raise
    
    def gethistorybyplaca(self, placa):
        """Obtiene el historial de declaraciones de un establecimiento por placa.

        Args:
            placa (str): Placa de identificación del establecimiento.

        Raises:
            ValueError: No se encontraron declaraciones para la placa _placa_.
            ValueError: Los datos proporcionados no son correctos.

        Returns:
            dict: Respuesta de la API de TNS, los campos son:
                    - OTIPO: tipo de pago
                    - OPERIODO: periodo de pago
                    - OFECHA: fecha de pago
                    - OTOTALPAGO: total pagado
                    - OESTADO: estado en el momento (no lo sé)
        """
        try:
            return self.make_request(
                method='get',
                queryparams={
                    'placa': placa
                },
                endpoint=self.endpoints['ica']['historial'],
                api_err_message='Ha ocurrido un error',
                custom_err_message=f'No se han encontrado historico de pagos asociados a la plata *{placa}*'
            )
        except Exception as e:
            raise

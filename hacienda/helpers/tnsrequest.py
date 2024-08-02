import requests
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
            # get the environment variables
            envs = self.__env()

            # queryparams for the request
            request = f'empresa={envs['empresa']}&usuario={envs['usuario']}&password={envs['password']}&tnsapitoken={envs['tnsapitoken']}&documento={cc}'

            # make the request to tns 
            response = self.request.get(f'{self.url}{self.endpoints["prediales"]['listar']}?{request}')

            if response.status_code >= 400 and response.status_code <= 500:
                error = response.json()

                if 'No se encontraron predios'.lower() in error['results'].lower():
                    raise ValueError('*No se encontraron predios para el documento 1091352585.*')
                
                raise ValueError('Estamos teniendo problemas con el servicio, por favor intente más tarde.')
            

            return response.json()
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
            # obtiene las variables de entorno
            envs = self.__env()

            # estructura de la request
            request = f'empresa={envs['empresa']}&usuario={envs['usuario']}&password={envs['password']}&tnsapitoken={envs['tnsapitoken']}&ficha={ficha}'

            response = self.request.post(f'{self.url}{self.endpoints["prediales"]["pdf"]}?{request}')

            if response.status_code >= 400 and response.status_code <= 500:
                raise ValueError('Estamos teniendo problemas con el servicio, por favor intente más tarde.')

            return response.json()

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
            envs = self.__env()
            request = f'{self.endpoints['ica']['establecimientos']}?empresa={envs['empresa']}&usuario={envs['usuario']}&password={envs['password']}&tnsapitoken={envs['tnsapitoken']}&documento={cc}'
            response = self.request.get(f'{self.url}{request}')

            if response.status_code >= 400 and response.status_code <= 500:
                error = response.json()

                if 'No se encontro el establecimiento'.lower() in error['results'].lower():
                    raise ValueError(error['results'])
                
                raise ValueError('Estamos teniendo problemas con el servicio, por favor intente más tarde.')

            # si todo sale bien, retornamos la respuesta
            return response.json()
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
            envs = self.__env()
            request = f'{self.endpoints['ica']['historial']}?empresa={envs['empresa']}&usuario={envs['usuario']}&password={envs['password']}&tnsapitoken={envs['tnsapitoken']}&placa={placa}'
            response = self.request.get(f'{self.url}{request}')

            if response.status_code >= 400 and response.status_code <= 500:
                error = response.json()

                if 'Ha ocurrido un error'.lower() in error['results'].lower():
                    raise ValueError('Los datos proporcionados no son correctos.')
                
                raise ValueError('Los datos proporcionados no son correctos.')

            return response.json()
        except Exception as e:
            raise

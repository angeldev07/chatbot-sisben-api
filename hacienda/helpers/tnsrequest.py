import requests
import os 
from dotenv import load_dotenv

load_dotenv()

class TNSRequest:
    def __init__(self):
        """
            Inicializa la instancia de TNSRequest con la URL base y los endpoints disponibles.
        """
        self.url = "https://api-gov.tns.co/api/Predial/"
        self.endpoints = {
            'prediales': 'ListarPrediosDocumento',
            'reporte': 'GenRecTemporalFicha',
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
            response = self.request.get(f'{self.url}{self.endpoints["prediales"]}?{request}')

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

            response = self.request.post(f'{self.url}{self.endpoints["reporte"]}?{request}')

            if response.status_code >= 400 and response.status_code <= 500:
                raise ValueError('Estamos teniendo problemas con el servicio, por favor intente más tarde.')

            return response.json()

        except Exception as e:
            raise
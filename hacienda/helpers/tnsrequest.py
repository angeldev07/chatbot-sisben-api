import requests
import os 
from dotenv import load_dotenv

load_dotenv()

class TNSRequest:
    def __init__(self):
        self.url = "https://api-gov.tns.co/api/Predial/"
        self.endpoints = {
            'prediales': 'ListarPrediosDocumento',
            'reporte': 'GenRecTemporalFicha',
        }
        self.request = requests

    def __env(self):
        return {
            'empresa': os.environ.get('CODIGO_EMPRESA'),
            'usuario': os.environ.get('USUARIO'),
            'password': os.environ.get('PASSWD'),
            'tnsapitoken': os.environ.get('TNSTOKEN'),
        }

    def getprediales(self, cc):
        try:
            # get the environment variables
            envs = self.__env()

            # queryparams for the request
            request = f'empresa={envs['empresa']}&usuario={envs['usuario']}&password={envs['password']}&tnsapitoken={envs['tnsapitoken']}&documento={cc}'

            # make the request to tns 
            response = self.request.get(f'{self.url}{self.endpoints["prediales"]}?{request}')

            if response.status_code >= 400 and response.status_code < 500:
                error = response.json()

                if 'No se encontraron predios'.lower() in error['results'].lower():
                    raise ValueError('*No se encontraron predios para el documento 1091352585.*')
                
                raise ValueError(error['Estamos teniendo problemas con el servicio, por favor intente más tarde.'])
            

            return response.json()
        except Exception as e:
            raise

    def getpaymethod(self, ficha):
        try:
            # obtiene las variables de entorno
            envs = self.__env()

            # estructura de la request
            request = f'empresa={envs['empresa']}&usuario={envs['usuario']}&password={envs['password']}&tnsapitoken={envs['tnsapitoken']}&ficha={ficha}'

            response = self.request.post(f'{self.url}{self.endpoints["reporte"]}?{request}')

            # raise error if status code is not 200
            response.raise_for_status()

            return response.json()

        except Exception as e:
            raise
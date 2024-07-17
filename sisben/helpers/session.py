import requests
from bs4 import BeautifulSoup

class SisbenSession():

    def __init__(self):
        self.initial_url = 'https://reportes.sisben.gov.co/dnp_sisbenconsulta'
        self.session = requests.Session()
        self.verify_token = self.get_token_from_request()

    def get_types_document(self):
        return {
            '1': 'Registro Civil',
            '2': 'Tarjeta de Identidad',
            '3': 'Cédula de Ciudadanía',
            '4': 'Cédula de Extranjería',
            '5': 'DNI (Pais de origen)',
            '6': 'DNI (Pasaporte)',
            '7': 'Salvoconducto para refugiado',
            '8': 'Permiso Especial de Permanencia',
            '9': 'Permiso Por Protección Temporal'
        }


    def get_token_from_request(self):
        """Extrae el token de la página web para realizar la consulta del Sisben.

        Returns:
            str: Token de la página web.
        """
        try:
            response = self.session.get(self.initial_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
            return token
        except Exception as e:
            return str('No se pudo concretar la consulta del Sisben. Intente más tarde.')
        
    def make_request(self, docType, docNumber):
        try:
            data = {
                '__RequestVerificationToken': self.verify_token,
                'TipoID': docType,
                'documento': docNumber,
            }
            response = self.session.post(self.initial_url, data=data, cookies=self.session.cookies)
            
            if response.status_code != 200:
                raise ValueError('Lo sentimos, estamos teniendo problemas con la consulta del Sisben. Intentelo más tarde. Si el problema persiste, comuníquese con el administrador del servicio.')
            
            return response
        except Exception as e:
            raise
    
    def get_sisben(self, docType, docNumber):
        try:
            res = self.make_request(docType, docNumber)

            soup = BeautifulSoup(res.content, 'html.parser')

            fecha_consulta = soup.find('p', class_='campo1 text-right rounded font-weight-bold float-right')

            if fecha_consulta is None:
                raise ValueError(f'El tipo de identificación: {self.get_types_document()[str(docType)]}, con el número de documento: {docNumber}. NO se encuentra en la base del Sisben IV')
            
            fecha_consulta = soup.find('p', class_='campo1 text-right rounded font-weight-bold float-right').text.strip()
            ficha = soup.find_all('p', class_='campo1 text-right rounded font-weight-bold float-right')[1].text.strip()
            puntaje = soup.find('p', class_='text-uppercase font-weight-bold text-white').text.strip()
            nivel_pobreza = soup.find('p', class_='text-center font-weight-bold').text.strip()

            # Extraer información adicional
            nombres = soup.find('p', string='Nombres:').find_next_sibling('p').text.strip()
            apellidos = soup.find('p', string='Apellidos:').find_next_sibling('p').text.strip()
            tipo_documento = soup.find('p', string='Tipo de documento:').find_next_sibling('p').text.strip()
            numero_documento = soup.find('p', string='Número de documento:').find_next_sibling('p').text.strip()
            municipio = soup.find('p', string='Municipio:').find_next_sibling('p').text.strip()
            departamento = soup.find('p', string='Departamento:').find_next_sibling('p').text.strip()

            return {
                'status_code': res.status_code,
                'sisben': {
                    'fecha_consulta': fecha_consulta,
                    'ficha': ficha,
                    'puntaje': puntaje,
                    'nivel_pobreza': nivel_pobreza,
                },
                'persona': {
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'tipo_documento': tipo_documento.strip(),
                    'numero_documento': numero_documento.strip(),
                    'municipio': municipio.strip(),
                    'departamento': departamento.strip(),
                }
            }
        except Exception as e:
            raise
    
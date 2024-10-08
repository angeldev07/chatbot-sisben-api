import requests
from bs4 import BeautifulSoup
from sisben.helpers.logs import write_log

class SisbenSession():

    def __init__(self):
        self.initial_url = 'https://reportes.sisben.gov.co/dnp_sisbenconsulta'
        self.critical_error_mssg = 'Lo sentimos, la pagina del Sisben no responde en este momento. Por favor, intenta de nuevo mas tarde.'
        self.session = requests.Session()
        try:
            self.verify_token = self.get_token_from_request()
        except Exception as e:
            write_log(f'Error al iniciar la sesión: {str(e)}', 500, '')
            self.verify_token = None

    def reset_session(self):
        self.session.close() # Cerrar la sesión actual
        # Crear una nueva sesión y obtenemos el token de esa nueva sesión
        self.session = requests.Session()
        try:
            self.verify_token = self.get_token_from_request()
        except Exception as e:
            write_log(f'Error al reiniciar la sesión en reset session: {str(e)}', 500, '')
            self.verify_token = None
    
    def close_session(self):
        if self.session:
            self.session.close()

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
            response = self.session.get(self.initial_url, timeout=5)

           
            if response.status_code != 200:
                write_log('Error al obtener el token en get_token_from_request', response.status_code, '')
                return None

            # si no ocurre una excepción, se extrae el token
            soup = BeautifulSoup(response.content, 'html.parser')
            token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
            return token
        except Exception as e:
            return None
        
    def make_request(self, docType, docNumber):
        max_try = 4 # Número máximo de intentos para obtener una respuesta exitosa
        
        for attempt in range(max_try):
            try:
                if self.verify_token is None:
                    # intento maximo de 5 veces para obtener una conexión exitosa y obtener el token
                    for _ in range(2):
                        self.reset_session()
                        if self.verify_token is not None:
                            break
                    else:
                        write_log('Se intento la conexion 5 veces y no se obtuvo respuesta exitosa en  make_request', 500, '')
                        raise ValueError(self.critical_error_mssg)

                data = {
                    '__RequestVerificationToken': self.verify_token,
                    'TipoID': docType,
                    'documento': docNumber,
                }

                response = self.session.post(self.initial_url, data=data, timeout=5, cookies=self.session.cookies)

                if response.status_code == 200:
                    return response
                else:
                    write_log(f'Intento {attempt + 1} de conexion fallido en make_request', response.status_code, '')
        
            except Exception as e:
                write_log(f"Error en el intento {attempt + 1}: {str(e)} en make_request", 500, '')
            
        raise ValueError(self.critical_error_mssg)
    
    def get_sisben(self, docType, docNumber):
        try:
            res = self.make_request(docType, docNumber)

            soup = BeautifulSoup(res.content, 'html.parser')

            fecha_consulta = soup.find('p', class_='campo1 text-right rounded font-weight-bold float-right')

            if fecha_consulta is None:
                raise ValueError(f'El tipo de identificación: {self.get_types_document()[str(docType)]}, con el número de documento: {docNumber}. NO se encuentra en la base del Sisben IV')
            
            # datos del sisben IV
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

            # Encontrar el registo valido
            registro_valido = soup.find('div', string='Registro válido')
            
            if registro_valido:
                registro_valido = True
            else:
                registro_valido = False

            # Encontrar y extraer el contenido del <strong>
            card_body = soup.find('div', class_='card-body border border-dark border border-5')
            if card_body:
                strong_text = card_body.find('strong').text.strip()
            else:
                strong_text = None

            # Extraer información de contacto
            nombre_administrador = soup.find('p', string='Nombre administrador:').find_next_sibling('p').text.strip()
            direccion = soup.find('p', string='Dirección:').find_next_sibling('p').text.strip()
            telefono = soup.find('p', string='Teléfono:').find_next_sibling('p').text.strip()
            correo_electronico = soup.find('p', string='Correo Electrónico:').find_next_sibling('p').text.strip()

            return {
                'status_code': res.status_code,
                'sisben': {
                    'fecha_consulta': fecha_consulta,
                    'ficha': ficha,
                    'puntaje': puntaje,
                    'nivel_pobreza': nivel_pobreza,
                    'registro': {
                        'valido': registro_valido,
                        'text': strong_text
                    }
                },
                'persona': {
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'tipo_documento': tipo_documento.strip(),
                    'numero_documento': numero_documento.strip(),
                    'municipio': municipio.strip(),
                    'departamento': departamento.strip(),
                },
                'contacto': {
                    'nombre_administrador': nombre_administrador,
                    'direccion': direccion,
                    'telefono': telefono,
                    'correo_electronico': correo_electronico,
                }
            }
        except Exception as e:
            raise 
    
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
        self.url = "https://api-gov.tns.co/v2/"
        self.endpoints = {
            "prediales": {
                "listar": "Predial/ListarPrediosDocumento",
                "pdf": "Predial/GenRecTemporalFicha",
            },
            "ica": {
                "establecimientos": "Local/ListarEstablecimientosDocumento",
                "historial": "Local/GetAllDeclaracionesPlaca",
            },
        }
        self.request = requests
        self.token = None  # Token de autenticación

    def __env(self):
        """
        Obtiene las variables de entorno necesarias para la autenticación en el API.

        Returns:
            dict: Un diccionario con las variables de entorno de autenticación.
        """
        return {
            "empresa": os.environ.get("CODIGO_EMPRESA"),
            "usuario": os.environ.get("USUARIO"),
            "password": os.environ.get("PASSWD"),
            "tnsapitoken": os.environ.get("TNSTOKEN"),
        }

    def __get_auth_token(self):
        """
        Obtiene un nuevo token de autenticación desde la API de TNS.

        Returns:
            str: Token de autenticación.

        Raises:
            ValueError: Si hay un problema obteniendo el token.
        """
        try:
            envs = self.__env()
            login_url = f"{self.url}Acceso/SolicitarToken"
            params = {
                "empresa": envs["empresa"],
                "usuario": envs["usuario"],
                "password": envs["password"],
            }

            response = self.request.get(login_url, params=params)

            if response.status_code == 200:
                # La API retorna el token como texto plano
                token = response.text.strip()
                self.token = token
                return token
            else:
                raise ValueError(
                    f"Error al obtener el token de autenticación: {response.status_code}"
                )

        except Exception as e:
            raise ValueError(f"Error al obtener el token de autenticación: {str(e)}")

    def geturlrequest(self, queryparams: dict):
        """Obtiene la url final para hacer la peticion a la api de tns

        Args:
            queryparams (dict): Los query params que necesita la API.

        Returns:
            str: La url completa para hacer la petición con los query params
        """
        if not queryparams:
            return ""

        params = []
        for key, value in queryparams.items():
            params.append(f"{key}={value}")

        return "&".join(params)

    def __is_session_expired(self, response: Response):
        """
        Verifica si la respuesta indica que la sesión ha caducado.

        Args:
            response (Response): La respuesta HTTP a verificar.

        Returns:
            bool: True si la sesión ha caducado, False en caso contrario.
        """
        if response.status_code == 401:
            try:
                error_data = response.json()
                return (
                    error_data.get("status") == False
                    and "sesión ha caducado" in error_data.get("message", "").lower()
                )
            except:
                return False
        return False

    def validate_response(
        self, response: Response, api_err_message: str, custom_err_message: str
    ):
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
            # Intentar parsear el contenido como JSON
            try:
                error = response.json()
                # Verificar si el mensaje de error específico está en la respuesta
                if api_err_message and (
                    api_err_message.lower() in error.get("results", "").lower()
                ):
                    raise ValueError(custom_err_message)
            except ValueError:
                # Si ocurre un error al intentar parsear JSON, manejarlo como texto plano
                error_text = response.text
                if api_err_message and (api_err_message.lower() in error_text.lower()):
                    raise ValueError(custom_err_message)
                raise ValueError("Error inesperado en el servidor: " + error_text)

            raise ValueError(
                "Estamos teniendo problemas con el servicio, por favor intente más tarde."
                if not custom_err_message
                else custom_err_message
            )

        # Retornar la respuesta JSON si el estado no es de error
        return response.json()

    def make_request(
        self,
        endpoint: str,
        queryparams: dict,
        method: str,
        api_err_message: str = None,
        custom_err_message: str = None,
    ):
        """
            Realiza la petición a la API de tns
        Args:
            endpoint (str): endpoint a hacer la peticion. Se encuentra en la propiedad endpoints
            queryparams (dict): queryparams necesarios para hacer la peticion.
            method (str): metodo http a realizar
            api_err_message (str): Un trozo del mensaje de error que retorna la api de tns en caso de querer enviar mensajes personalizados
            custom_err_message (str): Mensaje de error personalizado.

        Raises:
            ValueError: Mensaje de error personalizado en caso de que se envie.

        Returns:
            json: Retorna un json de la peticion en caso de que se responda con status 200.
        """
        max_login_attempts = 2
        login_attempts = 0

        while login_attempts < max_login_attempts:
            try:
                # Obtener token si no existe
                if not self.token:
                    self.__get_auth_token()

                # Preparar headers con autenticación
                headers = {"Authorization": f"{self.token}"}

                # Construir URL con query params
                request_params = self.geturlrequest(queryparams)
                url = f"{self.url}{endpoint}"
                if request_params:
                    url += f"?{request_params}"

                # Realizar petición
                if method.lower() == "get":
                    response = self.request.get(url, headers=headers)
                elif method.lower() == "post":
                    response = self.request.post(url, headers=headers)
                else:
                    raise ValueError("Método no permitido.")

                # Verificar si la sesión ha caducado
                if self.__is_session_expired(response):
                    login_attempts += 1
                    if login_attempts < max_login_attempts:
                        # Limpiar token y reintentar
                        self.token = None
                        continue
                    else:
                        raise ValueError(
                            "No se pudo renovar la sesión después de 2 intentos."
                        )

                # Validar respuesta
                return self.validate_response(
                    response=response,
                    api_err_message=api_err_message,
                    custom_err_message=custom_err_message,
                )

            except ValueError as ve:
                # Si es un error de validación de respuesta, re-lanzar
                if "renovar la sesión" in str(ve):
                    raise
                if login_attempts >= max_login_attempts:
                    raise
                # Si es otro tipo de ValueError, incrementar intentos y continuar
                login_attempts += 1
                if login_attempts < max_login_attempts:
                    self.token = None
                    continue
                raise
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
                method="get",
                queryparams={"documento": cc},
                endpoint=self.endpoints["prediales"]["listar"],
                api_err_message="No se encontraron predios",
                custom_err_message=f"No se han encontrado predios relacionados para el documento {cc}",
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
                method="post",
                queryparams={"ficha": ficha},
                endpoint=self.endpoints["prediales"]["pdf"],
                api_err_message="Algo ha fallado: No fue posible generar factura",
                custom_err_message="¡Te felicito! estas al día con tus impuestos, de esta manera estás contribuyendo para hacer de Villa del Rosario, una ciudad posible.",
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
                method="get",
                queryparams={"documento": cc},
                endpoint=self.endpoints["ica"]["establecimientos"],
                api_err_message="No se encontro el establecimiento",
                custom_err_message=f"No se han encontrado establecimientos comerciales asociados al documenot *{cc}*",
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
                method="get",
                queryparams={"placa": placa},
                endpoint=self.endpoints["ica"]["historial"],
                api_err_message="Ha ocurrido un error",
                custom_err_message=f"No se han encontrado historico de pagos asociados a la placa *{placa}*",
            )
        except Exception as e:
            raise

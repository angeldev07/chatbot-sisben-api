import os
from django.conf import settings
import requests
from bs4 import BeautifulSoup


class SecretariaDesarrollo:
    """
    Clase que contiene las urls de la secretaria de desarrollo
    """

    """
        Url base para realizar las peticiones a la secretaria de desarrollo
    """

    baseurl = "http://201.130.16.28:8080/home/acciones.php"

    """Session para realizar las peticiones a la secretaria de desarrollo
    """
    session = requests.Session()

    def __exist__user__(self, html):
        """
        Método que verifica si el usuario existe en la base de datos de la secretaria de desarrollo
        """
        soup = BeautifulSoup(html, "html.parser")
        input_certificado = soup.find("input", {"name": "certificado"})

        return input_certificado  # Si el input no existe, el usuario no existe

    def __get__certificado__(self, numDoc):
        res = self.session.get(
            "http://201.130.16.28:8080/home/rud/certificado.php",
            cookies=self.session.cookies,
        )

        if res.status_code == 200 and "application/pdf" in res.headers.get(
            "Content-Type", ""
        ):
            # Guardar el contenido en un archivo PDF
            file_path = os.path.join(
                settings.MEDIA_ROOT, f"certificadorud-{numDoc}.pdf"
            )
            with open(file_path, "wb") as f:
                f.write(res.content)
                return settings.MEDIA_URL + f"certificadorud-{numDoc}.pdf"

        else:
            return None

    def getungrudcertificate(self, cedula):
        # Hacer la primera petición
        initial_url = self.baseurl + "?accion=BtnLogRud&documento=" + cedula
        res = self.session.get(
            initial_url
        )  # Hacer la petición para saber si el usuario existe

        if res.status_code != 200:
            return {
                "mensaje": "Error al obtener el certificado de la secretaria de desarrollo"
            }

        if self.__exist__user__(res.content) is None:
            return {"mensaje": f"El número de documento {cedula} no existe en el RUD"}

        certificado_url = self.__get__certificado__(cedula)
        self.session.close()
        return {"mensaje": f'http://localhost:8000{certificado_url}' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}{certificado_url}'}

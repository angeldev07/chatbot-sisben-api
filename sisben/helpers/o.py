import requests
from bs4 import BeautifulSoup

# URL de la página inicial
initial_url = 'https://reportes.sisben.gov.co/dnp_sisbenconsulta'

# Iniciar una sesión
session = requests.Session()

# Obtener la página inicial para extraer el token de verificación
response = session.get(initial_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extraer el token de verificación desde un input hidden
token = soup.find('input', {'name': '__RequestVerificationToken'})['value']

# Configurar los datos del formulario
data = {
    '__RequestVerificationToken': token,
    'TipoID': '3',
    'documento': '1091352585',
}

# URL del formulario
form_url = 'https://reportes.sisben.gov.co/dnp_sisbenconsulta'

# Enviar la solicitud POST con los datos del formulario
response = session.post(form_url, data=data, cookies=session.cookies)

print(response.status_code)

# Analizar la respuesta HTML
soup = BeautifulSoup(response.content, 'html.parser')

print(soup)

# Extraer la información relevante existente
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

print(f'Fecha de consulta: {fecha_consulta}')
print(f'Ficha: {ficha}')
print(f'Puntaje: {puntaje}')
print(f'Nivel de pobreza: {nivel_pobreza}')
print(f'Nombres: {nombres}')
print(f'Apellidos: {apellidos}')
print(f'Tipo de documento: {tipo_documento}')
print(f'Número de documento: {numero_documento}')
print(f'Municipio: {municipio}')
print(f'Departamento: {departamento}')

session.close()

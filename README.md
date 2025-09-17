# 🤖 Chatbot Sisben API - Alcaldía Villa del Rosario

API REST desarrollada en Django para el chatbot "Rosario" de la Alcaldía de Villa del Rosario. Proporciona servicios integrados para consultas de Sisben, prediales de hacienda, ICA y certificados de desarrollo urbano.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación](#instalación)
  - [Desarrollo Local](#desarrollo-local)
  - [Producción con Docker](#producción-con-docker)
- [Configuración](#configuración)
- [Uso](#uso)
- [Endpoints de la API](#endpoints-de-la-api)
- [Autenticación](#autenticación)
- [Documentación](#documentación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Contribución](#contribución)

## 🚀 Características

- **Consultas Sisben**: Validación y consulta de información del sistema Sisben por tipo y número de documento
- **Servicios de Hacienda**: 
  - Consulta de prediales por cédula
  - Generación de reportes PDF de prediales
  - Enlaces de pago en línea
- **Servicios ICA**:
  - Consulta de locales comerciales por cédula
  - Historial de establecimientos por placa
- **Secretaría de Desarrollo**: Certificados de desarrollo urbano (GRUD)
- **Autenticación por API Key**
- **Documentación automática con Swagger**
- **Soporte para archivos estáticos y media**
- **Configuración para desarrollo y producción**

## 🛠️ Tecnologías

- **Backend**: Django 5.0.7 + Django REST Framework 3.15.2
- **Base de Datos**: SQLite (configurable)
- **Documentación**: drf-yasg (Swagger/OpenAPI)
- **Servidor**: Gunicorn
- **Contenedores**: Docker & Docker Compose
- **Generación PDF**: WeasyPrint
- **Procesamiento de imágenes**: Pillow
- **CORS**: django-cors-headers
- **Archivos estáticos**: WhiteNoise

## 📦 Requisitos del Sistema

### ⚠️ **IMPORTANTE - Compatibilidad de Python**

Este proyecto **requiere Python 3.12 o anterior**. **NO es compatible con Python 3.13** debido a dependencias que requieren compilación de C++ y aún no tienen soporte para Python 3.13.

### Requisitos Mínimos

- **Python**: 3.8 - 3.12 (recomendado 3.12.3)
- **pip**: 21.0+
- **Git**: Para clonar el repositorio
- **Docker & Docker Compose**: Para despliegue en producción (opcional)

### Dependencias del Sistema (para WeasyPrint)

#### Windows
```bash
# Instalar Visual C++ Build Tools o Visual Studio
# Descargar desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
```

#### macOS
```bash
brew install python@3.12 cairo pango gdk-pixbuf libffi
```

## 🔧 Instalación

### Desarrollo Local

#### 1. Clonar el repositorio
```bash
git clone https://github.com/angeldev07/chatbot-sisben-api.git
cd chatbot-sisben-api
```

#### 2. Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Verificar versión de Python
```bash
python --version
# Debe mostrar Python 3.8.x - 3.12.x
```

#### 4. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Nota**: Si encuentras errores de compilación con WeasyPrint en Windows, instala primero las Visual C++ Build Tools.

#### 5. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

#### 7. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

La API estará disponible en: `http://127.0.0.1:8000`

### Producción con Docker

#### 1. Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
IP_SERVER=http://tu-dominio.com
CODIGO_EMPRESA=codigo_empresa_tns
USUARIO=usuario_tns
PASSWD=password_tns
TNSTOKEN=token_tns
```

#### 2. Construir y ejecutar con Docker Compose
```bash
# Crear red externa (solo la primera vez)
docker network create general

# Construir y ejecutar
docker-compose up -d --build
```

#### 3. Verificar despliegue
```bash
docker-compose logs -f chatbotavr
```

La API estará disponible en: `http://localhost:9010`

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `SECRET_KEY` | Clave secreta de Django | ✅ | `oqx(+js37!7(-5-b0ie+1k+_dl62p-kkp#9pzk0_nu=&0zbw6c` |
| `IP_SERVER` | URL del servidor en producción | ✅ | `http://api.ejemplo.com` |
| `CODIGO_EMPRESA` | Código de empresa para TNS | ✅ | `123456` |
| `USUARIO` | Usuario para servicios TNS | ✅ | `usuario_tns` |
| `PASSWD` | Contraseña para servicios TNS | ✅ | `password_tns` |
| `TNSTOKEN` | Token de autenticación TNS | ✅ | `token_secreto` |

### Configuraciones por Entorno

#### Desarrollo (`settings/development.py`)
- `DEBUG = True`
- Base de datos SQLite local
- CORS habilitado para localhost
- Archivos estáticos servidos por Django

#### Producción (`settings/production.py`)
- `DEBUG = False`
- Configuración desde variables de entorno
- Logging avanzado
- WhiteNoise para archivos estáticos
- CORS configurado para dominios específicos

## 🔐 Autenticación

La API utiliza autenticación por API Key. Para generar una clave:

### Desarrollo
```bash
./generateapi.sh
# Seleccionar opción 1 (Desarrollo)
# Ingresar nombre de usuario
```

### Producción
```bash
./generateapi.sh
# Seleccionar opción 2 (Producción)
# Ingresar nombre de usuario
```

### Uso de API Key
Incluir en las cabeceras de todas las peticiones:
```
X-API-Key: TU_API_KEY_AQUI
```

## 📖 Uso

### Ejemplo de Consulta Sisben
```bash
curl -X GET "http://localhost:8000/api/sisben/consultar?docType=3&docNumber=12345678" \
     -H "X-API-Key: TU_API_KEY"
```

### Ejemplo de Consulta Prediales
```bash
curl -X GET "http://localhost:8000/api/hacienda/prediales?cedula=12345678" \
     -H "X-API-Key: TU_API_KEY"
```

## 🛣️ Endpoints de la API

### Sisben
- `GET/POST /api/sisben/consultar` - Consultar información Sisben
- `GET/POST /api/sisben/validar` - Validar datos Sisben

### Hacienda
- `GET/POST /api/hacienda/prediales` - Consultar prediales por cédula
- `GET/POST /api/hacienda/predial-reporte` - Generar reporte PDF de prediales
- `GET/POST /api/hacienda/predial-pago` - Obtener enlace de pago
- `GET/POST /api/hacienda/ica-locales` - Consultar locales ICA por cédula
- `GET/POST /api/hacienda/ica-historial` - Historial ICA por placa

### Secretaría de Desarrollo
- `GET/POST /api/secretaria-desarrollo/certificado-grud` - Certificado GRUD

### Utilidades
- `GET /tns-predial-pago-online/<short_id>/` - Redirección a enlaces de pago cortos

## 📚 Documentación

### Swagger UI
Accede a la documentación interactiva en:
- **Desarrollo**: http://127.0.0.1:8000/doc
- **Producción**: http://tu-dominio.com/doc

### Admin Panel
- **Desarrollo**: http://127.0.0.1:8000/admin
- **Producción**: http://tu-dominio.com/admin

## 📁 Estructura del Proyecto

```
chatbot-sisben-api/
├── 📄 manage.py                      # Script principal de Django
├── 📄 requirements.txt               # Dependencias Python
├── 📄 Dockerfile                     # Configuración Docker
├── 📄 docker-compose.yml             # Orquestación Docker
├── 📄 entrypoint.sh                  # Script de inicialización
├── 📄 gunicorn_config.py             # Configuración Gunicorn
├── 📄 generateapi.sh                 # Script para generar API Keys
├── 📄 bd-delete-prediales.py         # Utilidad de limpieza BD
├── 📁 chatbot/                       # Configuración principal Django
│   ├── 📄 __init__.py
│   ├── 📄 asgi.py                    # Configuración ASGI
│   ├── 📄 urls.py                    # URLs principales
│   ├── 📄 wsgi.py                    # Configuración WSGI
│   └── 📁 settings/                  # Configuraciones por entorno
│       ├── 📄 __init__.py
│       ├── 📄 base.py                # Configuración base
│       ├── 📄 development.py         # Configuración desarrollo
│       └── 📄 production.py          # Configuración producción
├── 📁 sisben/                        # App Sisben
│   ├── 📄 models.py                  # Modelos de datos
│   ├── 📄 views.py                   # Vistas/Controladores
│   ├── 📄 urls.py                    # URLs del módulo
│   ├── 📁 helpers/                   # Utilidades Sisben
│   ├── 📁 utils/                     # Funciones utilitarias
│   ├── 📁 templates/                 # Plantillas HTML
│   └── 📁 migrations/                # Migraciones BD
├── 📁 hacienda/                      # App Hacienda
│   ├── 📄 models.py                  # Modelos prediales/ICA
│   ├── 📄 views.py                   # Vistas exportadas
│   ├── 📄 urls.py                    # URLs del módulo
│   ├── 📁 view/                      # Controladores específicos
│   │   ├── 📄 prediales.py           # Lógica prediales
│   │   └── 📄 ica.py                 # Lógica ICA
│   ├── 📁 helpers/                   # Utilidades Hacienda
│   ├── 📁 utils/                     # Transformadores datos
│   ├── 📁 management/                # Comandos Django
│   └── 📁 migrations/                # Migraciones BD
├── 📁 secretaria_desarrollo/         # App Secretaría
│   ├── 📄 models.py                  # Modelos certificados
│   ├── 📄 views.py                   # Vistas certificados
│   ├── 📄 urls.py                    # URLs del módulo
│   ├── 📁 utils/                     # Lógica específica
│   └── 📁 migrations/                # Migraciones BD
├── 📁 shared/                        # Utilidades compartidas
│   ├── 📁 auth/                      # Sistema autenticación
│   │   └── 📄 apikey.py              # Autenticación API Key
│   └── 📁 utils/                     # Utilidades generales
└── 📁 static/                        # Archivos estáticos
    └── 📁 img/                       # Imágenes del proyecto
```

## 🚀 Comandos Útiles

### Desarrollo
```bash
# Ejecutar servidor
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic

# Generar API Key
python manage.py generate_api_key nombre_usuario

# Ejecutar tests
python manage.py test
```

### Docker
```bash
# Construir imagen
docker-compose build

# Ejecutar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Ejecutar comando en contenedor
docker-compose exec chatbotavr python manage.py migrate
```

## 🐛 Solución de Problemas

### Error de compilación WeasyPrint en Windows
```bash
# Instalar Visual C++ Build Tools
# Luego reinstalar WeasyPrint
pip uninstall weasyprint
pip install weasyprint
```

### Error Python 3.13
```bash
# Verificar versión
python --version

# Si es 3.13, instalar 3.12
pyenv install 3.12.3
pyenv local 3.12.3
```

### Error de permisos en Linux
```bash
# Dar permisos a scripts
chmod +x generateapi.sh
chmod +x entrypoint.sh
```

### Error de puertos en Docker
```bash
# Verificar puertos ocupados
netstat -tlnp | grep :9010

# Cambiar puerto en docker-compose.yml si es necesario
```

## 📝 Notas Importantes

1. **Compatibilidad Python**: Solo hasta 3.12.x debido a dependencias C++
2. **Variables de entorno**: Requeridas para producción
3. **API Keys**: Necesarias para todas las peticiones
4. **CORS**: Configurado para desarrollo, ajustar en producción
5. **Base de datos**: SQLite por defecto, configurable para PostgreSQL/MySQL
6. **Archivos estáticos**: Manejados por WhiteNoise en producción
7. **Logs**: Configurados en `/logs/` en producción

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto es propiedad de la Alcaldía de Villa del Rosario.

## 📧 Contacto

Para soporte técnico, contactar al equipo de desarrollo de la Alcaldía de Villa del Rosario.

---

**Desarrollado con ❤️ para la Alcaldía de Villa del Rosario**

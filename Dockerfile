# Dockerfile

# Utiliza una imagen base oficial de Python
FROM python:3.12.3

ENV PYTHONUNBUFFERED=1

# instalar weasyprint
RUN apt-get update && apt-get install -y \
    weasyprint

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del proyecto a la imagen
COPY . .

# Expone el puerto que Gunicorn utilizará
EXPOSE 8000

# Comando para ejecutar Gunicorn
CMD ["sh", "entrypoint.sh"]

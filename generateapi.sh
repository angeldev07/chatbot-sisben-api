#!/bin/bash

# Pedir los datos necesarios
echo "Ingresa el nombre de usuario"
read username

echo -e "entorno: \n1.Desarrollo. \n2.Produccion. """
read environment

# Validar que el entorno esté dentro del rango permitido
if [[ $environment -lt 1 || $environment -gt 2 ]]; then
    echo "Opcion no valida."
fi

if [[ $environment -eq 1 ]]; then
    API_KEY=$(python3 manage.py generate_api_key $username --settings=chatbot.settings.development | tail -n 1)
    echo $API_KEY
fi

if [[ $environment -eq 2 ]]; then
    # Ejecutar el comando de Django dentro del contenedor Docker
    API_KEY=$(python3 manage.py generate_api_key $username --settings=chatbot.settings.production | tail -n 1)
    echo $API_KEY
fi

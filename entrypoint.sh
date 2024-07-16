#!/bin/sh

echo "Make migrations"
python3 manage.py makemigrations --settings=chatbot.settings.production

echo "Migrate"
python3 manage.py migrate --settings=chatbot.settings.production

echo "Run server"
gunicorn --env DJANGO_SETTINGS_MODULE=chatbot.settings.production chatbot.wsgi:application --config gunicorn_config.py
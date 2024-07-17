# gunicorn_config.py

bind = "0.0.0.0:8000"
workers = 8  # Número de workers, puede ajustarse según los recursos del servidor
accesslog = '-'
errorlog = '-'

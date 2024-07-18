from django.conf import settings
from datetime import datetime
import os

def write_log(response: str, status: int, url_request: str):
    log_file = os.path.join(settings.BASE_DIR, 'logs/response_logs.txt')
    with open(log_file, 'a') as file:
        time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        file.write(f'[ {time} ] - {url_request} - Return: {response} with status: {status} \n')
from django.core.management.base import BaseCommand
from hacienda.models import APIKey  

class Command(BaseCommand):
    help = 'Genera una API key para un usuario específico'
    def add_arguments(self, parser):
        parser.add_argument("username", type=str)

    def handle(self, *args, **kwargs):
        username = kwargs['username']

        if APIKey.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'Ya existe un usuario usando ese username. Intente de nuevo'))
            return
    
        new_api_key = APIKey.objects.create(
            username=username
        )
        self.stdout.write(self.style.SUCCESS(f'Generated API key: {new_api_key.key}'))

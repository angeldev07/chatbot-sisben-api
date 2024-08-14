from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed
from hacienda.models import APIKey

class APIKeyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.query_params.get('apiKey')

        if not api_key:
            raise AuthenticationFailed('Acceso denegado. Por favor, ingrese una apikey valida.')
        
        if not APIKey.objects.filter(key=api_key).exists():
            raise AuthenticationFailed('Acceso denegado. Por favor, ingrese una apikey valida.')

        return True

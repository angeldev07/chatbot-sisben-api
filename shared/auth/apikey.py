from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed

class APIKeyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.query_params.get('apiKey')

        if not api_key:
            raise AuthenticationFailed('Acceso denegado. Por favor, ingrese una apikey valida.')
        
        return True

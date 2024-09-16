from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from hacienda.view.prediales import redirectToOriginalLink
import os


schema_view = get_schema_view(
   openapi.Info(
      title="API del Chatbot 'Rosario' para la Alcaldia Villa del Rosario.",
      default_version='v1',
      description="Documentación de la API para los servicios de Hacienda y Sisben para el chatbot Rosario.",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   url='http://localhost:8000/' if settings.DEBUG else f'{os.environ.get('IP_SERVER')}/',
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sisben/', include('sisben.urls')),
    path('api/hacienda/', include('hacienda.urls')),
    path('tns-predial-pago-online/<str:short_id>/', redirectToOriginalLink, name='redirectToOriginalLink'),
    path('api/secretaria-desarrollo/', include('secretaria_desarrollo.urls')),
    # swagger
    path('doc', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

# Esto debería estar fuera del bloque if settings.DEBUG
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

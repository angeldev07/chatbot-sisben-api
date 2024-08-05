from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hacienda.view.prediales import redirectToOriginalLink
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sisben/', include('sisben.urls')),
    path('api/hacienda/', include('hacienda.urls')),
    path('tns-predial-pago-online/<str:short_id>/', redirectToOriginalLink, name='redirectToOriginalLink'),
]

# Esto debería estar fuera del bloque if settings.DEBUG
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
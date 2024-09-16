from django.urls import path
from .views import getungrudcertificate

urlpatterns = [
    path("certificado-grud", getungrudcertificate),
]

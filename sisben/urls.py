from django.urls import path
from . import views

urlpatterns = [
    path('consultar', views.sisben, name='get the sisben data'),
    path('validar', views.validate_sisben, name='validate the sisben data')
]
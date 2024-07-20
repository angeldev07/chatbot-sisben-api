from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_message, name='get a message'),
    path('consultar', views.sisben, name='get the sisben data'),
    path('validar', views.validate_sisben, name='validate the sisben data'),
    path('consultar_pdf', views.sisben_pdf, name='get the sisben data in pdf'),
]
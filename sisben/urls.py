from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_message, name='get a message'),
    path('consultar', views.sisben, name='get the sisben data'),
]
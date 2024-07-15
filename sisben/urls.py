from django.urls import path
from . import views

urlpatterns = [
    path('consultar', views.sisben, name='get the sisben data'),
]
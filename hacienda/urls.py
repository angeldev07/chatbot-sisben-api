from django.urls import path
from hacienda.views import getprediales, getpredialpdf, getpaymethod

urlpatterns = [
    path('prediales', getprediales, name='get predials by cc'),
    path('predial-reporte', getpredialpdf, name='get the pdf to predial selection'),
    path('predial-pago', getpaymethod, name= 'Get the pay method link.')
]
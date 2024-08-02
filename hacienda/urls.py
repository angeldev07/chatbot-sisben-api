from django.urls import path
from hacienda.views import getprediales, getpredialpdf, getpaymethod, getpaymethoddirect, getpredialpdfdirect, getpredialdirect

urlpatterns = [
    path('prediales', getprediales, name='get predials by cc'),
    path('predial-reporte', getpredialpdf, name='get the pdf to predial selection'),
    path('predial-pago', getpaymethod, name= 'Get the pay method link.'),
    path('prediales-direct', getpredialdirect, name='get predials by cc'),
    path('predial-reporte-direct', getpredialpdfdirect, name='get the pdf to predial selection'),
    path('predial-pago-direct', getpaymethoddirect, name= 'Get the pay method link.')
]
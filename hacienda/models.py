from django.db import models

ESTADOS = {
   'CONSULTA_PREDIAL_GENERAL': 'CONSULTA_PREDIAL_GENERAL',
   'CONSULTA_PREDIAL_OBJETIVO': 'CONSULTA_PREDIAL_OBJETIVO',
   'GENERA_LIQUIDACION': 'GENERA_LIQUIDACION',
   'OBTIENE_LINK_PAGO' : 'OBTIENE_LINK_PAGO',
   'FINALIZO': 'FINALIZO'
}

class PredialSearch(models.Model):
    cedula = models.CharField(max_length=20, blank=True, null=True)
    prediales = models.TextField(blank=True, null=True)
    link_cobro = models.TextField(blank=True, null=True)
    primera_consulta = models.DateTimeField( blank=True, null=True)
    estado = models.CharField(max_length=254, blank=True, null=True)
    mensaje = models.TextField(blank=True, null=True)
    nombre_archivo = models.CharField(max_length=254, blank=True, null=True)

    class Meta:
        db_table = 'prediales'

#This class is use to reduce the tns pay link.
class PredialUrlShort(models.Model):
    original_url = models.TextField(blank=True, null=True)
    short_id = models.CharField(max_length=20, blank=True, null=True, unique=True)

    class Meta:
        db_table = 'prdiales-links-pagos'

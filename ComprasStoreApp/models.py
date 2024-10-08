from django.db import models
from .choices import TIPO_IMPUESTO, TIPO_DOCUMENTO
from ProveedoresStoreApp.models import Proveedor

# Create your models here.


class Compras(models.Model):
    id_compras = models.AutoField(primary_key=True)
    num_documento = models.CharField(max_length=15, unique=True)
    fecha = models.DateField()
    total = models.IntegerField()
    tipo_documento = models.CharField(
        max_length=20, choices=TIPO_DOCUMENTO, default="BOLETA"
    )
    tipo_impuesto = models.CharField(
        max_length=20, choices=TIPO_IMPUESTO, default="CON IMPUESTO"
    )
    proveedor_FK = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "compras"

    def __str__(self):
        return f"{self.num_documento}"

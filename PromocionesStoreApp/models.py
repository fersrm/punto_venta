from django.db import models
from ProductosStoreApp.models import Producto

# Create your models here.


class Promociones(models.Model):
    id_promocion = models.AutoField(primary_key=True)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    descuento = models.IntegerField()
    producto_FK = models.ForeignKey(Producto, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "promociones"

    def __str__(self):
        return f"{self.id_promocion}"

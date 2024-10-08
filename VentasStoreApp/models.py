from django.db import models

# son para borrar imagen al actualizar
from django.contrib.auth.models import User
from ProductosStoreApp.models import Producto

# Create your models here.


class Ventas(models.Model):
    id_venta = models.AutoField(primary_key=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    usuario_FK = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "ventas"


class Boletas(models.Model):
    id_boleta = models.AutoField(primary_key=True)
    total_boleta = models.IntegerField()
    total_descuento = models.IntegerField(default=0)
    venta_FK = models.ForeignKey(Ventas, on_delete=models.CASCADE, default=1)

    class Meta:
        db_table = "boletas"

    def __str__(self):
        return f"{self.id_boleta}"


class DetalleBoletas(models.Model):
    id_detalle_boleta = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    total = models.IntegerField()
    producto_FK = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    # Campos adicionales para almacenar datos del producto
    producto_nombre = models.CharField(max_length=255)
    producto_precio = models.IntegerField()
    boleta_FK = models.ForeignKey(Boletas, on_delete=models.CASCADE, default=1)

    class Meta:
        db_table = "detalleboleta"

    def __str__(self):
        return f"{self.id_detalle_boleta}"

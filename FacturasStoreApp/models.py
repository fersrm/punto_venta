from django.db import models

# son para borrar imagen al actualizar
from ClientesStoreApp.models import Cliente
from ProductosStoreApp.models import Producto
from VentasStoreApp.models import Ventas


# Create your models here.


class Facturas(models.Model):
    id_factura = models.AutoField(primary_key=True)
    total_factura = models.IntegerField()
    total_descuento = models.IntegerField(default=0)
    cliente_fk = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    venta_FK = models.ForeignKey(Ventas, on_delete=models.CASCADE)

    class Meta:
        db_table = "facturas"

    def __str__(self):
        return f"{self.id_factura}"


class DetalleFacturas(models.Model):
    id_detalle_factura = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    total = models.IntegerField()
    producto_FK = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    # Campos adicionales para almacenar datos del producto
    producto_nombre = models.CharField(max_length=255)
    producto_precio = models.IntegerField()
    factura_FK = models.ForeignKey(Facturas, on_delete=models.CASCADE, default=1)

    class Meta:
        db_table = "detallefactura"

    def __str__(self):
        return f"{self.id_detalle_factura}"

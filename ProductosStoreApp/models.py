from django.db import models
from .choices import TIPO_MEDIDA, TIPO_IMPUESTO
from django.contrib.auth.models import User

# son para borrar imagen al actualizar
from django.core.files.storage import default_storage
from utils.custom_img import resize_image, crop_image
import uuid
import os


# Create your models here.


def dynamic_upload_path(instance, filename):
    random_filename = str(uuid.uuid4())
    extension = os.path.splitext(filename)[1]
    return f"productos/{random_filename}{extension}"


# -----------------------Productos----------------


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=45, unique=True)

    class Meta:
        db_table = "categoria"

    def __str__(self):
        return f"{self.nombre_categoria}"


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    codigo_producto = models.CharField(max_length=45, unique=True)
    descripcion_producto = models.CharField(max_length=45)
    precio_bruto_producto = models.IntegerField()
    precio_venta = models.IntegerField(default=10)
    margen_ganancia = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    imagen = models.ImageField(
        upload_to=dynamic_upload_path, null=True, blank=True, default=None
    )
    stock = models.DecimalField(max_digits=10, decimal_places=3, default=10.000)
    fecha = models.DateField(auto_now_add=True)
    tipo_medida = models.CharField(max_length=20, choices=TIPO_MEDIDA, default="UNIDAD")
    tipo_impuesto = models.CharField(
        max_length=20, choices=TIPO_IMPUESTO, default="IVA"
    )
    usuario_FK = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    categoria_FK = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):

        if self.pk:
            self.handle_old_image()

        super(Producto, self).save(*args, **kwargs)

        if self.imagen and os.path.exists(self.imagen.path):
            resize_image(self.imagen.path, 500)
            crop_image(self.imagen.path, 500)

    def handle_old_image(self):
        old_profile = Producto.objects.get(pk=self.pk)
        if old_profile.imagen and old_profile.imagen.path != self.imagen.path:
            default_storage.delete(old_profile.imagen.path)

    class Meta:
        db_table = "producto"

    def __str__(self):
        return f"{self.descripcion_producto}"

from django.db import models
from ProductosStoreApp.models import Producto
from django.core.files.storage import default_storage
from utils.custom_img import resize_image, crop_image
import uuid
import os

# Create your models here.
## Revisar margen global


def empresa_picture_path(instance, filename):
    random_filename = str(uuid.uuid4())
    extension = os.path.splitext(filename)[1]
    return f"empresa/{random_filename}{extension}"


class DatosEmpresa(models.Model):
    id_datos_empresa = models.AutoField(primary_key=True)
    nombre_empresa = models.CharField(max_length=45)
    rut_empresa = models.CharField(max_length=15)
    email = models.EmailField(max_length=64)
    telefono = models.CharField(max_length=15)
    comuna = models.CharField(max_length=45)
    direccion_empresa = models.CharField(max_length=45)
    razon_social = models.CharField(max_length=64)
    actividad_economica = models.CharField(max_length=64)
    IVA = models.IntegerField()
    image = models.ImageField(
        upload_to=empresa_picture_path, null=True, blank=True, default=None
    )
    margen_global = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    def save(self, *args, **kwargs):
        try:
            original_instance = DatosEmpresa.objects.get(pk=1)
        except DatosEmpresa.DoesNotExist:
            original_instance = None

        if original_instance and self.margen_global != original_instance.margen_global:
            margen = self.margen_global

            productos = Producto.objects.all()
            for producto in productos:
                producto.precio_venta = float(
                    producto.precio_bruto_producto
                    * (1 + (margen + producto.margen_ganancia) / 100)
                )
                producto.precio_venta = round(producto.precio_venta)
                producto.save()

        if self.pk and self.image:
            self.handle_old_image()

        super(DatosEmpresa, self).save(*args, **kwargs)

        if self.image and os.path.exists(self.image.path):
            resize_image(self.image.path, 300)
            crop_image(self.image.path, 300)

    def handle_old_image(self):
        old_profile = DatosEmpresa.objects.get(pk=self.pk)
        if old_profile.image and old_profile.image.path != self.image.path:
            default_storage.delete(old_profile.image.path)

    class Meta:
        db_table = "datosempresa"

    def __str__(self):
        return f"{self.nombre_empresa}"

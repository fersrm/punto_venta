from django.db import models

# Create your models here.


class Giro(models.Model):
    id_giro = models.AutoField(primary_key=True)
    tipo_giro = models.CharField(max_length=45)

    class Meta:
        db_table = "giro"

    def __str__(self):
        return f"{self.tipo_giro}"


class Rubro(models.Model):
    id_rubro = models.AutoField(primary_key=True)
    tipo_rubro = models.CharField(max_length=45)

    class Meta:
        db_table = "rubro"

    def __str__(self):
        return f"{self.tipo_rubro}"


class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    run_proveedor = models.CharField(max_length=15, unique=True)
    nombre_proveedor = models.CharField(max_length=45)
    razon_social = models.CharField(max_length=45)
    correo_proveedor = models.EmailField(max_length=64, unique=True)
    telefono_proveedor = models.CharField(max_length=45)
    contacto = models.CharField(max_length=45)
    direccion = models.CharField(max_length=45)
    giro_FK = models.ForeignKey(Giro, on_delete=models.SET_NULL, null=True)
    rubro_FK = models.ForeignKey(Rubro, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "proveedor"

    def __str__(self):
        return f"{self.nombre_proveedor}"

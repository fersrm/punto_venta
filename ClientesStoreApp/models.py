from django.db import models

# Create your models here.


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    run_cliente = models.CharField(max_length=15, unique=True)
    nombre_cliente = models.CharField(max_length=45)
    apellido_cliente = models.CharField(max_length=45)
    correo_cliente = models.EmailField(max_length=64, unique=True)
    telefono_cliente = models.CharField(max_length=15)
    direccion = models.CharField(max_length=45)

    class Meta:
        db_table = "cliente"

    def __str__(self):
        return f"{self.nombre_cliente} {self.apellido_cliente}"

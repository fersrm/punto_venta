from django.contrib import admin
from VentasStoreApp.models import Boletas, Ventas

# Clase base de administración con el método común

# Registro de Boletas


@admin.register(Boletas)
class BoletasAdmin(admin.ModelAdmin):
    list_display = ("id_boleta", "total_boleta")


# Registro de Ventas


@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    list_display = ("id_venta", "fecha_emision", "usuario_FK")

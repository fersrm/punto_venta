from django.contrib import admin
from PromocionesStoreApp.models import Promociones

# Clase base de administración con el método común


@admin.register(Promociones)
class PromocionesAdmin(admin.ModelAdmin):
    list_display = ("id_promocion", "descuento", "producto_FK", "activo")

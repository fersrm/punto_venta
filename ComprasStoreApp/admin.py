from django.contrib import admin
from .models import Compras

# Clase base de administración con el método común


@admin.register(Compras)
class ComprasAdmin(admin.ModelAdmin):
    list_display = (
        "id_compras",
        "num_documento",
    )

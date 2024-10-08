from django.contrib import admin
from .models import Proveedor, Giro, Rubro

# Clase base de administración con el método común

# -------------------------PROVEEDOR--------------------------


@admin.register(Giro)
class GiroAdmin(admin.ModelAdmin):
    pass


@admin.register(Rubro)
class RubroAdmin(admin.ModelAdmin):
    pass


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
        "id_proveedor",
        "run_proveedor",
        "nombre_proveedor",
        "telefono_proveedor",
    )

from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "id_cliente",
        "run_cliente",
        "nombre_cliente",
        "apellido_cliente",
        "telefono_cliente",
    )

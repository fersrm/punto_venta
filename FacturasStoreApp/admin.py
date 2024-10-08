from django.contrib import admin
from FacturasStoreApp.models import Facturas


@admin.register(Facturas)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("id_factura", "total_factura")

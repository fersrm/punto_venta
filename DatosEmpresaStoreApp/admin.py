from django.contrib import admin
from DatosEmpresaStoreApp.models import DatosEmpresa


@admin.register(DatosEmpresa)
class DatosEmpresaAdmin(admin.ModelAdmin):
    list_display = ("rut_empresa", "nombre_empresa", "email")

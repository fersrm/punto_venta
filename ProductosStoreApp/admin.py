from django.contrib import admin
from ProductosStoreApp.models import Producto, Categoria

# -----------------PRODUCTOS----------------
# Registro de Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    pass


# Registro de Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    readonly_fields = ("fecha",)

    def categoria(self, obj):
        return getattr(obj, "categoria_FK")

    categoria.short_description = "Categoria"
    list_display = (
        "id_producto",
        "codigo_producto",
        "descripcion_producto",
        "precio_bruto_producto",
        "categoria",
    )

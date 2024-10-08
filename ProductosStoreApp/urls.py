from django.urls import path
from ProductosStoreApp import views

urlpatterns = [
    # ---------CRUD PRODUCTOS----------------------
    path("", views.ProductoListView.as_view(), name="Tienda"),
    path("agregar/", views.AgregarProductoView.as_view(), name="agregar_prodcuto"),
    path(
        "editar/<int:pk>/", views.EditarProductoView.as_view(), name="editar_producto"
    ),
    path(
        "borrar/<int:pk>/",
        views.EliminarProductoView.as_view(),
        name="eliminar_producto",
    ),
    # -------------AÑADIDO PRODUCTOS----------------
    path("plus/<int:pk>/", views.PlusProductoView.as_view(), name="añadir_producto"),
    # ---------------NOTIFICACIONES------------------
    path("tabla_stock/", views.TablaStockView.as_view(), name="tabla_stock"),
    path(
        "producto/<int:pk>/",
        views.ProductoDetailView.as_view(),
        name="producto_detalle",
    ),
    path("carga_excel/", views.CargaProductosExcelView.as_view(), name="carga_excel"),
]

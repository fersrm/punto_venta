from django.urls import path
from ProveedoresStoreApp import views

urlpatterns = [
    # ------------CRUD PROVEEDOR--------------------
    path("", views.ProveedorListView.as_view(), name="Proveedores"),
    path("agregar/", views.AgregarProveedorView.as_view(), name="agregar_proveedor"),
    path(
        "editar/<int:pk>/", views.EditarProveedorView.as_view(), name="editar_proveedor"
    ),
    path(
        "borrar/<int:pk>/",
        views.EliminarProveedorView.as_view(),
        name="eliminar_proveedor",
    ),
]

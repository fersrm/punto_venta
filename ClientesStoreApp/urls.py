from django.urls import path
from ClientesStoreApp import views

urlpatterns = [
    # ------------CRUD USUARIOS--------------------
    path("", views.CLienteListView.as_view(), name="Clientes"),
    path("agregar/", views.AgregarClientesView.as_view(), name="agregar_cliente"),
    path("editar/<int:pk>/", views.EditarCLientesView.as_view(), name="editar_cliente"),
    path(
        "borrar/<int:pk>/", views.EliminarClienteView.as_view(), name="eliminar_cliente"
    ),
]

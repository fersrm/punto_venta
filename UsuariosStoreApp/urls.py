from django.urls import path
from UsuariosStoreApp import views

urlpatterns = [
    # ------------CRUD USUARIOS--------------------
    path("", views.UsuarioListView.as_view(), name="Usuarios"),
    path("agregar/", views.AgregarUsuarioView.as_view(), name="agregar_usuario"),
    path("editar/<int:pk>/", views.EditarUsuarioView.as_view(), name="editar_usuario"),
    path(
        "borrar/<int:pk>/", views.EliminarUsuarioView.as_view(), name="eliminar_usuario"
    ),
    path("perfil/", views.ProfileUpdateView.as_view(), name="Profile"),
    path("cambio_clave/", views.PasswordChangeView.as_view(), name="CambioPass"),
]

from django.urls import path
from ComprasStoreApp import views

urlpatterns = [
    # ---------------------------------------------
    path("", views.AgregarCompraView.as_view(), name="Compras"),
    path("compra/<int:pk>/", views.CompraProductoView.as_view(), name="añadir_compra"),
]

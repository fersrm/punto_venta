from django.urls import path
from DatosEmpresaStoreApp import views


urlpatterns = [
    path("", views.EditarDatosEmpresaView.as_view(), name="Setting"),
]

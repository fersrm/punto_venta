from django.urls import path
from django.contrib.auth.views import LoginView
from SistemaStoreApp import views

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("", views.HomeView.as_view(), name="Home"),
    path("salir/", views.SalirView.as_view(), name="salir"),
    path(
        "exportar-top-mas-vendidos/",
        views.ExportTopMasVendidosExcel.as_view(),
        name="export_top_mas_vendidos_excel",
    ),
    path(
        "exportar-top-menos-vendidos/",
        views.ExportTopMenosVendidosExcel.as_view(),
        name="export_top_menos_vendidos_excel",
    ),
]

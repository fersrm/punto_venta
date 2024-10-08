from django.urls import path
from VentasStoreApp import views


urlpatterns = [
    path("", views.VentasBoletaListView.as_view(), name="Ventas"),
    path("informe_boletas/", views.BoletaListView.as_view(), name="Boletas"),
    path("informes/", views.InformesListView.as_view(), name="Informes"),
    path(
        "boletas/<int:pk>/detalle/",
        views.DetalleBoletaView.as_view(),
        name="detalle_boleta",
    ),
    path(
        "boletas/exportar/pdf/",
        views.ExportBoletasPDFView.as_view(),
        name="exportar_boletas_pdf",
    ),
    path(
        "boletas/exportar/excel/",
        views.ExportBoletasExcelView.as_view(),
        name="exportar_boletas_excel",
    ),
    path(
        "informes/exportar/pdf/",
        views.ExportVentasRangoPDFView.as_view(),
        name="exportar_rango_pdf",
    ),
    path(
        "informes/exportar/excel/",
        views.ExportVentasRangoExcelView.as_view(),
        name="exportar_rango_excel",
    ),
]

from django.urls import path
from FacturasStoreApp import views


urlpatterns = [
    path("", views.VentasFacturasListView.as_view(), name="Facturas"),
    path("informe_factura/", views.FacturaListView.as_view(), name="Informe_facturas"),
    path(
        "facturas/exportar/pdf/",
        views.ExportFacturasPDFView.as_view(),
        name="exportar_facturas_pdf",
    ),
    path(
        "facturas/exportar/excel/",
        views.ExportFacturasExcelView.as_view(),
        name="exportar_facturas_excel",
    ),
    path(
        "facturas/<int:pk>/detalle/",
        views.DetalleFacturaView.as_view(),
        name="detalle_factura",
    ),
]

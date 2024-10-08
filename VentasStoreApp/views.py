from django.views.generic import ListView, CreateView, View, DetailView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Subquery, OuterRef, IntegerField, Value
from django.db.models.functions import Coalesce

# Permisos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# Modelos y formularios
from .models import Boletas, Ventas, DetalleBoletas
from .forms import VentasForm
from ProductosStoreApp.models import Producto
from FacturasStoreApp.models import Facturas
from PromocionesStoreApp.models import Promociones

# funciones
from utils.helpers import buscar_fecha_rango, buscar_venta, buscar_fecha
from utils.custom_ventas import (
    carrito_json,
    procesar_carrito,
    verificar_stock_y_calcular_total,
)

# Create your views here.

# -----------------------Ventas Boletas--------------------


class VentasBoletaListView(LoginRequiredMixin, CreateView, ListView):
    model = Ventas
    form_class = VentasForm
    template_name = "pages/boletas/boletas.html"

    def form_valid(self, form):
        usuario_logeado = self.request.user
        venta = form.save(commit=False)
        venta.usuario_FK = usuario_logeado

        # Obtener Carrito
        carrito = carrito_json(form.cleaned_data["carrito"])

        try:
            total_boleta, total_descuento = verificar_stock_y_calcular_total(carrito)
        except ValueError as e:
            print(e)
            error_message = "Falta de Stock en productos cargados, vuelva a cargarlos"
            return self.form_invalid(form, custom_message=error_message)

        # Crear la boleta y la venta
        venta.save()
        boleta = Boletas(
            total_boleta=total_boleta, total_descuento=total_descuento, venta_FK=venta
        )
        boleta.save()

        # Procesar carrito y crear detalles de boleta
        procesar_carrito(carrito, boleta, DetalleBoletas, "boleta_FK")

        success_message = "Venta Generada con Éxito"
        messages.success(self.request, success_message, extra_tags="success-venta")
        return super().form_valid(form)

    def form_invalid(self, form, custom_message=None):
        # Si no se proporciona un mensaje personalizado, usar el mensaje por defecto
        if custom_message:
            messages.error(self.request, custom_message)
        else:
            messages.error(self.request, "Error en el formulario")

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")

        return HttpResponseRedirect("/ventas/")

    def get_success_url(self):
        return reverse_lazy("Ventas")

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar")
        producto_queryset = Producto.objects.filter(codigo_producto__exact=busqueda)

        if producto_queryset.exists() and busqueda:
            now = timezone.now().date()

            # Subquery para obtener el primer descuento de la promoción activa
            subquery_descuento = (
                Promociones.objects.filter(
                    producto_FK=OuterRef("pk"), activo=True, fecha_termino__gte=now
                )
                .order_by("fecha_inicio")
                .values("descuento")[:1]
            )

            # Anotar el descuento o 0 si no hay promoción activa
            producto_queryset = producto_queryset.annotate(
                descuento=Coalesce(
                    Subquery(subquery_descuento), Value(0), output_field=IntegerField()
                )
            )

        elif not producto_queryset.exists() and busqueda:
            messages.error(self.request, f"No existe producto con el código {busqueda}")

        return producto_queryset.first()


# --------------INFORME Ventas---------------------


class InformesListView(LoginRequiredMixin, PermitsPositionMixin, ListView):
    model = Boletas
    template_name = "pages/ventas/informes.html"

    def get_queryset(self):
        fecha1 = self.request.GET.get("buscarFecha1")
        fecha2 = self.request.GET.get("buscarFecha2")

        queryset = buscar_fecha_rango(self.model, fecha1, fecha2, Facturas)

        return queryset


# --------------INFORME PDF BOLETAS ---------------------


class BoletaListView(LoginRequiredMixin, PermitsPositionMixin, ListView):
    model = Boletas
    template_name = "pages/boletas/informes/informeBoleta.html"

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar")
        busqueda_fecha = self.request.GET.get("buscarFecha")
        campos_busqueda = ["id_boleta", "total_boleta"]
        if busqueda_fecha:
            queryset = buscar_fecha(self.model, busqueda_fecha)
        else:
            queryset = buscar_venta(self.model, campos_busqueda, busqueda)
        queryset = queryset.order_by("-id_boleta")
        return queryset


########################## DETALLE ##########################


class DetalleBoletaView(LoginRequiredMixin, PermitsPositionMixin, DetailView):
    model = Boletas
    template_name = "pages/boletas/informes/detalle_boleta.html"
    context_object_name = "boleta"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detalle_boletas"] = DetalleBoletas.objects.filter(
            boleta_FK=self.object
        )
        return context


##########################################
###### DESCARGA DE INFORMES ##############
##########################################

############## PDF #######################
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_CENTER


class ExportBoletasPDFView(LoginRequiredMixin, PermitsPositionMixin, View):
    model = Boletas

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="boletas.pdf"'

        buffer = response
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Obtener los datos
        boletas = self.model.objects.all()

        # Encabezado centrado
        styles = getSampleStyleSheet()
        styles["Heading1"].alignment = TA_CENTER
        header = Paragraph("Reporte de Boletas", styles["Heading1"])
        elements.append(header)

        # Tabla de datos
        data = [["ID Boleta", "Total", "Vendedor", "Fecha de Emisión"]]
        for boleta in boletas:
            data.append(
                [
                    boleta.id_boleta,
                    boleta.total_boleta,
                    str(boleta.venta_FK.usuario_FK.username),
                    boleta.venta_FK.fecha_emision.strftime("%d-%m-%Y"),
                ]
            )

        table = Table(data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(table)

        # Construir el PDF
        doc.build(elements)
        return response


class ExportVentasRangoPDFView(LoginRequiredMixin, PermitsPositionMixin, View):
    model_boleta = Boletas

    def get(self, request, *args, **kwargs):
        # Preparar la respuesta de PDF
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="ventas_rango.pdf"'

        buffer = response
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Encabezado centrado
        styles = getSampleStyleSheet()
        styles["Heading1"].alignment = TA_CENTER
        header = Paragraph("Reporte de Ventas por Rango de Fechas", styles["Heading1"])
        elements.append(header)

        # Obtener las fechas desde la URL
        fecha1 = request.GET.get("buscarFecha1")
        fecha2 = request.GET.get("buscarFecha2")

        # Generar el reporte de ventas por rango de fechas
        ventas_totales = buscar_fecha_rango(self.model_boleta, fecha1, fecha2, Facturas)

        # Tabla de datos
        data = [["Fecha", "Total Ventas"]]
        for fecha, total in ventas_totales.items():
            data.append([fecha, total])

        table = Table(data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(table)

        # Construir el PDF
        doc.build(elements)
        return response


############# Excel ############
import pandas as pd


class ExportBoletasExcelView(LoginRequiredMixin, PermitsPositionMixin, View):
    model = Boletas

    def get(self, request, *args, **kwargs):
        # Obtener los datos
        boletas = self.model.objects.all().values(
            "id_boleta",
            "total_boleta",
            "venta_FK__usuario_FK__username",
            "venta_FK__fecha_emision",
        )
        df = pd.DataFrame(list(boletas))

        # Separar la fecha y la hora
        df["Fecha"] = df["venta_FK__fecha_emision"].apply(
            lambda x: x.strftime("%d-%m-%Y")
        )
        df["Hora"] = df["venta_FK__fecha_emision"].apply(
            lambda x: x.strftime("%H:%M:%S")
        )

        # Eliminar la columna original con fecha y hora
        df = df.drop(columns=["venta_FK__fecha_emision"])

        # Renombrar columnas
        df.columns = ["ID Boleta", "Total", "Vendedor", "Fecha", "Hora"]

        # Crear respuesta con Excel
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="boletas.xlsx"'
        df.to_excel(response, index=False, engine="openpyxl")

        return response


class ExportVentasRangoExcelView(LoginRequiredMixin, View):
    model_boleta = Boletas

    def get(self, request, *args, **kwargs):
        # Obtener las fechas desde la URL
        fecha1 = request.GET.get("buscarFecha1")
        fecha2 = request.GET.get("buscarFecha2")

        # Generar el reporte de ventas por rango de fechas

        ventas_totales = buscar_fecha_rango(self.model_boleta, fecha1, fecha2, Facturas)

        # Crear DataFrame con los resultados
        df = pd.DataFrame(ventas_totales.items(), columns=["Fecha", "Total Ventas"])

        # Preparar la respuesta de Excel
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="ventas_rango.xlsx"'

        # Exportar el DataFrame a Excel
        df.to_excel(response, index=False, engine="openpyxl")

        return response

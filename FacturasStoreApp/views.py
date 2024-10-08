from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, View, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Subquery, OuterRef, IntegerField, Value
from django.db.models.functions import Coalesce

# Permisos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# Modelos y formularios
from .models import Facturas, Ventas, DetalleFacturas, Cliente
from .forms import VentasFacturasForm

# Modelo de productos y promociones
from ProductosStoreApp.models import Producto
from PromocionesStoreApp.models import Promociones

# funciones
from utils.helpers import buscar_venta, buscar_fecha
from utils.custom_ventas import (
    carrito_json,
    verificar_stock_y_calcular_total,
    procesar_carrito,
)

# -----------------------Ventas Factura--------------------


class VentasFacturasListView(LoginRequiredMixin, CreateView, ListView):
    model = Ventas
    form_class = VentasFacturasForm
    template_name = "pages/facturas/facturas.html"

    def form_valid(self, form):
        usuario_logeado = self.request.user
        venta = form.save(commit=False)
        venta.usuario_FK = usuario_logeado

        # Obtener Cliente ---------------------------
        cliente = form.cleaned_data["cliente_id"]
        # Convertir el valor a una instancia de Cliente
        cliente_instance = get_object_or_404(Cliente, pk=cliente)
        # --------------------------------------------

        # Obtener Carrito
        carrito = carrito_json(form.cleaned_data["carrito"])

        try:
            # Verificar stock y calcular el total de la boleta
            total_factura, total_descuento = verificar_stock_y_calcular_total(carrito)
        except ValueError as e:
            # Capturar el error de stock y mostrar un mensaje de error
            print(e)
            error_message = "Falta de Stock en productos cargados, vuelva a cargarlos"
            return self.form_invalid(form, custom_message=error_message)

        # Factura la boleta y la venta
        venta.save()
        factura = Facturas(
            total_factura=total_factura,
            total_descuento=total_descuento,
            venta_FK=venta,
            cliente_fk=cliente_instance,
        )
        factura.save()

        # Procesar carrito y crear detalles de boleta
        procesar_carrito(carrito, factura, DetalleFacturas, "factura_FK")

        success_message = "Venta Generada con Éxito"
        messages.success(self.request, success_message, extra_tags="success-factura")
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
        return reverse_lazy("Facturas")

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar")
        busqueda_cliente = self.request.GET.get("buscar_cliente")

        cliente = self.get_cliente_queryset(busqueda_cliente)
        producto = self.get_producto_queryset(busqueda)

        if not producto and busqueda:
            messages.error(self.request, f"No existe {busqueda}")
        elif not cliente and busqueda_cliente:
            messages.error(self.request, f"No existe {busqueda_cliente}")

        return producto or cliente or []

    def get_producto_queryset(self, busqueda):
        if not busqueda:
            return None

        producto_queryset = Producto.objects.filter(codigo_producto__exact=busqueda)
        if not producto_queryset.exists():
            return None

        # Validamos si la promoción ha expirado
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

        # Retornar el primer producto (asumiendo que solo quieres uno)
        return producto_queryset.first()

    def get_cliente_queryset(self, busqueda_cliente):
        if not busqueda_cliente:
            return None

        queryset_cliente = Cliente.objects.filter(run_cliente__exact=busqueda_cliente)
        return queryset_cliente.first() if queryset_cliente.exists() else None


# --------------INFORME PDF facturas ---------------------


class FacturaListView(LoginRequiredMixin, PermitsPositionMixin, ListView):
    model = Facturas
    template_name = "pages/facturas/informes/informeFactura.html"

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar")
        busqueda_f = self.request.GET.get("buscarFecha")
        campos_busqueda = ["id_factura", "total_factura"]
        if busqueda_f:
            queryset = buscar_fecha(self.model, busqueda_f)
        else:
            queryset = buscar_venta(self.model, campos_busqueda, busqueda)
        queryset = queryset.order_by("-id_factura")
        return queryset


########################## DETALLE ##########################


class DetalleFacturaView(LoginRequiredMixin, PermitsPositionMixin, DetailView):
    model = Facturas
    template_name = "pages/facturas/informes/detalle_factura.html"
    context_object_name = "factura"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detalle_facturas"] = DetalleFacturas.objects.filter(
            factura_FK=self.object
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


class ExportFacturasPDFView(LoginRequiredMixin, PermitsPositionMixin, View):
    model = Facturas

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="facturas.pdf"'

        buffer = response
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Obtener los datos
        facturas = self.model.objects.all()

        # Encabezado centrado
        styles = getSampleStyleSheet()
        styles["Heading1"].alignment = TA_CENTER
        header = Paragraph("Reporte de facturas", styles["Heading1"])
        elements.append(header)

        # Tabla de datos
        data = [["ID Factura", "Total", "Vendedor", "Fecha de Emisión"]]
        for factura in facturas:
            data.append(
                [
                    factura.id_factura,
                    factura.total_factura,
                    str(factura.venta_FK.usuario_FK.username),
                    factura.venta_FK.fecha_emision.strftime("%d-%m-%Y"),
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


############# Excel ############
import pandas as pd


class ExportFacturasExcelView(LoginRequiredMixin, PermitsPositionMixin, View):
    model = Facturas

    def get(self, request, *args, **kwargs):
        # Obtener los datos
        facturas = self.model.objects.all().values(
            "id_factura",
            "total_factura",
            "venta_FK__usuario_FK__username",
            "venta_FK__fecha_emision",
        )
        df = pd.DataFrame(list(facturas))

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
        df.columns = ["ID Factura", "Total", "Vendedor", "Fecha", "Hora"]

        # Crear respuesta con Excel
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="facturas.xlsx"'
        df.to_excel(response, index=False, engine="openpyxl")

        return response

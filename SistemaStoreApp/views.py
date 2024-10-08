from django.utils import timezone
from django.contrib.auth.views import LogoutView
from django.views.generic import ListView, View
from django.urls import reverse_lazy
from django.db.models import Q

# Modelos
from VentasStoreApp.models import Boletas, DetalleBoletas
from ComprasStoreApp.models import Compras
from ProductosStoreApp.models import Producto
from FacturasStoreApp.models import Facturas, DetalleFacturas
from django.contrib.auth.models import User
from UsuariosStoreApp.models import Profile

# Permisos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# funciones
from utils.helpers import top_productos, total_dia, total_ventas

# Create your views here.


class HomeView(LoginRequiredMixin, ListView):
    model = User
    template_name = "index.html"
    success_url = reverse_lazy("Home")

    def get_queryset(self):
        last_connected_users = User.objects.filter(
            Q(last_login__isnull=False)
        ).order_by("-last_login")[:5]
        return last_connected_users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agrega los usuarios activos al contexto
        recent_activity_cutoff = timezone.now() - timezone.timedelta(minutes=2)
        active_users = Profile.objects.filter(
            last_activity__gte=recent_activity_cutoff
        ).values_list("user_FK", flat=True)
        context["active_users"] = active_users

        user = active_users.first()
        print(f"user {user}")
        # Obtiene el valor de 'periodo' del parámetro GET
        periodo = self.request.GET.get("periodo", "dia")
        if periodo not in ["dia", "semana", "mes"]:
            periodo = "dia"

        ventas_diarias, compras_totales = total_ventas(
            Boletas, Compras, periodo, Facturas
        )

        context["ventas_diarias"] = ventas_diarias
        context["compras_totales"] = compras_totales
        context["mi_fecha"] = timezone.localtime(timezone.now()).date()

        # Boletas ---------------------------------
        boletas_data = total_dia(Boletas, "cantidad_boletas", "total_boleta")
        context.update(boletas_data)
        # Top Productos Ventas ---------------------
        campos_producto = (
            "codigo_producto",
            "descripcion_producto",
            "categoria_FK__nombre_categoria",
            "stock",
            "precio_venta",
        )

        top_mas_vendidos, top_menos_vendidos = top_productos(
            Producto, DetalleBoletas, campos_producto, DetalleFacturas
        )
        # Facturas ---------------------------------
        factura_data = total_dia(Facturas, "cantidad_factura", "total_factura")
        context.update(factura_data)

        context["top_mas_vendidos"] = top_mas_vendidos
        context["top_menos_vendidos"] = top_menos_vendidos
        return context


# --------------------SALIR---------------------


class SalirView(LogoutView):
    next_page = "/"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


#############################################
############# EXPORTAR A EXCEL ##############
#############################################

import pandas as pd
from django.http import HttpResponse


class BaseExportVendidosExcel(LoginRequiredMixin, PermitsPositionMixin, View):

    def obtener_productos(self, campos_producto):
        """
        Este método debe ser sobreescrito en las subclases para obtener el top más o menos vendidos.
        """
        raise NotImplementedError("Este método debe ser implementado en las subclases")

    def get(self, request, *args, **kwargs):
        # Validar por tipo de esquema

        campos_producto = (
            "codigo_producto",
            "descripcion_producto",
            "categoria_FK__nombre_categoria",
            "stock",
            "precio_venta",
        )

        # Llamar al método para obtener los productos vendidos
        productos = self.obtener_productos(campos_producto)

        # Crear un DataFrame de pandas
        data = [
            {
                "Código": (
                    p.get("codigo_producto")
                    if p.get("codigo_producto")
                    else p.get("producto_FK__codigo_producto")
                ),
                "Nombre de producto": (
                    p.get("descripcion_producto")
                    if p.get("descripcion_producto")
                    else p.get("producto_FK__descripcion_producto")
                ),
                "Categoría": (
                    p.get("categoria_FK__nombre_categoria")
                    if p.get("categoria_FK__nombre_categoria")
                    else p.get("producto_FK__categoria_FK__nombre_categoria")
                ),
                "Stock": (
                    float(p.get("stock", 0))
                    if p.get("stock")
                    else float(p.get("producto_FK__stock", 0))
                ),
                "Cantidad vendida": p.get("total_vendido", 0),
            }
            for p in productos
        ]

        df = pd.DataFrame(data)

        # Crear la respuesta HTTP con el archivo Excel
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.nombre_archivo}.xlsx"'
        )

        # Guardar el DataFrame en el archivo Excel
        df.to_excel(response, index=False)
        return response


class ExportTopMasVendidosExcel(BaseExportVendidosExcel):
    nombre_archivo = "top_mas_vendidos"

    def obtener_productos(self, campos_producto):
        top_mas_vendidos, _ = top_productos(
            Producto, DetalleBoletas, campos_producto, DetalleFacturas
        )

        return top_mas_vendidos


class ExportTopMenosVendidosExcel(BaseExportVendidosExcel):
    nombre_archivo = "top_menos_vendidos"

    def obtener_productos(self, campos_producto):
        _, top_menos_vendidos = top_productos(
            Producto, DetalleBoletas, campos_producto, DetalleFacturas
        )

        return top_menos_vendidos

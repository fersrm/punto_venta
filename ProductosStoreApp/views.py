# Librerías de Django
from django.views.generic import (
    ListView,
    UpdateView,
    DeleteView,
    CreateView,
    TemplateView,
    DetailView,
)
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Subquery, OuterRef, IntegerField, Value
from django.db.models.functions import Coalesce

# Permisos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# Modelos y formularios
from .forms import ProductoAgregarForm, ProductoEditarForm, PlusProductoForm
from .models import Producto
from PromocionesStoreApp.models import Promociones

# funciones
from utils.helpers import buscar_campos


# -----------------CRUD TIENDA-------------


class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "pages/productos/tienda.html"
    paginate_by = 5

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar")
        campos_busqueda = [
            "descripcion_producto",
            "codigo_producto",
            "stock",
            "categoria_FK__nombre_categoria",
        ]
        queryset = buscar_campos(self.model, campos_busqueda, busqueda)
        queryset = queryset.order_by("-id_producto")

        if not queryset and busqueda:
            messages.error(self.request, f"No Existe {busqueda}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now().date()

        # Paginación primero: obtener los productos de la página actual
        paginator = Paginator(context["object_list"], self.paginate_by)
        page = self.request.GET.get("page")
        paginated_products = paginator.get_page(page)

        # Obtener los IDs de los productos que están en la página actual
        product_ids = [producto.id_producto for producto in paginated_products]

        # Subquery para obtener el primer descuento de la promoción activa
        subquery_descuento = (
            Promociones.objects.filter(
                producto_FK=OuterRef("pk"), activo=True, fecha_termino__gte=now
            )
            .order_by("fecha_inicio")
            .values("descuento")[:1]
        )

        # Anotar el descuento o 0 si no hay promoción activa
        products_with_discount = Producto.objects.filter(
            id_producto__in=product_ids
        ).annotate(
            descuento=Coalesce(
                Subquery(subquery_descuento), Value(0), output_field=IntegerField()
            )
        )

        # Actualizar el contexto con los productos paginados y anotados
        context["object_list"] = products_with_discount
        context["page_obj"] = paginated_products

        return context


# -------------------------------------------------


class AgregarProductoView(LoginRequiredMixin, PermitsPositionMixin, CreateView):
    model = Producto
    form_class = ProductoAgregarForm
    template_name = "pages/productos/modal/AddTienda.html"

    def form_valid(self, form):
        # Obtener el usuario logeado
        usuario_logeado = self.request.user
        # Asignar el usuario logeado al campo usuario_FK antes de guardar
        producto = form.save(commit=False)
        producto.usuario_FK = usuario_logeado
        producto.margen_ganancia = (
            producto.margen_ganancia - self.request.datos_empresa.margen_global
        )

        producto.save()
        messages.success(self.request, "Producto agregado correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/tienda/")

    def get_success_url(self):
        return reverse_lazy("Tienda")


# --------------------------------------------------


class EditarProductoView(LoginRequiredMixin, PermitsPositionMixin, UpdateView):
    model = Producto
    form_class = ProductoEditarForm
    template_name = "pages/productos/modal/EditTienda.html"

    def form_valid(self, form):
        form.clean()
        producto = form.save(commit=False)
        producto.margen_ganancia = (
            producto.margen_ganancia - self.request.datos_empresa.margen_global
        )

        producto.save()
        messages.success(self.request, "Producto editado correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/tienda/")

    def get_success_url(self):
        return reverse_lazy("Tienda")


# -------------------------------------------------


class EliminarProductoView(LoginRequiredMixin, PermitsPositionMixin, DeleteView):
    model = Producto
    success_url = reverse_lazy("Tienda")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(self.request, "Producto eliminado correctamente")
        self.object.delete()
        return redirect(self.get_success_url())


# -----------------------------------------------------


class PlusProductoView(LoginRequiredMixin, PermitsPositionMixin, UpdateView):
    model = Producto
    form_class = PlusProductoForm
    template_name = "pages/productos/modal/PlusProduc.html"

    def form_valid(self, form):
        producto = form.instance
        stock_increment = form.cleaned_data.get("stock_increment")
        if stock_increment is not None:
            producto.stock += stock_increment
        form.save()
        messages.success(self.request, "Producto añadido correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/tienda/")

    def get_success_url(self):
        return reverse_lazy("Tienda")


# -----------------BAJO-STOCK-----------------------


class TablaStockView(LoginRequiredMixin, TemplateView):
    template_name = "components/modal/TablaReponerStock.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Acceder a los productos con stock bajo desde el contexto global
        context["object_list"] = self.request.productos_con_stock_bajo
        return context


########################## DETALLE ##########################


class ProductoDetailView(LoginRequiredMixin, PermitsPositionMixin, DetailView):
    model = Producto
    template_name = "pages/productos/detalle_producto.html"
    context_object_name = "boleta"
    context_object_name = "producto"


######################## CARGA DE PRODUCTOS POR EXCEL #################
import pandas as pd
from .forms import ProductosExcelForm
from django.db import transaction
from adapters.excel_adapter import ExcelAdapter
from django.views.generic import FormView
from .models import Categoria


class CargaProductosExcelView(LoginRequiredMixin, PermitsPositionMixin, FormView):
    model = Producto
    form_class = ProductosExcelForm
    template_name = "pages/productos/modal/carga_excel.html"
    success_url = reverse_lazy("Tienda")

    def form_valid(self, form):
        document = form.cleaned_data["document"]
        usuario_logeado = self.request.user

        try:
            df = pd.read_excel(document)

            with transaction.atomic():
                self.load_existing_data()
                error_list = self.process_dataframe(df, usuario_logeado)

            if error_list:
                for error in error_list:
                    messages.error(self.request, error, extra_tags="excel_error")

            messages.success(self.request, "Productos cargados correctamente")
            return redirect("Tienda")
        except Exception as e:
            print(e)
            messages.error(self.request, "Error al procesar el documento")
            return self.form_invalid(form)

    def load_existing_data(self):
        # Cargar productos existentes para evitar duplicados
        self.existing_products = Producto.objects.in_bulk(field_name="codigo_producto")

    def process_dataframe(self, df, usuario_logeado):
        error_list = []
        for index, row in df.iterrows():
            self.process_row(index, row, usuario_logeado, error_list)
        return error_list

    def process_row(self, index, row, usuario_logeado, error_list):
        try:
            adapter = ExcelAdapter(row)
            codigo_producto = adapter.get_codigo_producto()

            if codigo_producto in self.existing_products:
                error_list.append(
                    f"Error en la fila {index + 2}: El código de producto {codigo_producto} ya existe."
                )
                return

            producto = Producto(
                codigo_producto=codigo_producto,
                descripcion_producto=adapter.get_nombre_producto(),
                precio_bruto_producto=adapter.get_precio_proveedor(),
                precio_venta=adapter.get_precio_venta(),
                margen_ganancia=adapter.get_margen_ganancia(),
                stock=adapter.get_stock(),
                tipo_medida=adapter.get_tipo_medida(),
                tipo_impuesto=adapter.get_tipo_impuesto(),
                usuario_FK=usuario_logeado,
                categoria_FK=Categoria.objects.get(
                    nombre_categoria=adapter.get_categoria_producto()
                ),
            )

            producto.save()
            self.existing_products[producto.codigo_producto] = producto

        except Exception as e:
            print(e)
            error_message = f"Error en la fila {index + 2}: {str(e)}"
            error_list.append(error_message)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return redirect("Tienda")

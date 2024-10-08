# Librerías de Django
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy

# Permisos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# Modelos y formularios
from .forms import ComprasAgregarForm
from .models import Compras

# Modelos de productos
from ProductosStoreApp.models import Producto
from ProductosStoreApp.forms import PlusProductoForm


# Create your views here.


class AgregarCompraView(LoginRequiredMixin, PermitsPositionMixin, CreateView, ListView):
    model = Compras
    form_class = ComprasAgregarForm
    template_name = "pages/compras/compras.html"

    def form_valid(self, form):
        form.save()
        success_message = "Compra agregada correctamente"
        messages.success(self.request, success_message, extra_tags="success-alert")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.cleaned_data.get("num_documento"))
        print(form.clean())
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                print(field, error)
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/compras/")

    def get_success_url(self):
        return reverse_lazy("Compras")

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar")
        queryset = Producto.objects.filter(codigo_producto__exact=busqueda)

        if not queryset and busqueda:
            messages.error(self.request, f"No existe {busqueda}")

        queryset = queryset.first()
        return queryset


class CompraProductoView(LoginRequiredMixin, PermitsPositionMixin, UpdateView):
    model = Producto
    form_class = PlusProductoForm
    template_name = "pages/compras/modal/CompraProduc.html"

    def form_valid(self, form):
        producto = form.save(commit=False)
        stock_increment = form.cleaned_data.get("stock_increment")
        if stock_increment is not None:
            producto.stock += stock_increment
        form.save()
        success_message = "Producto añadido correctamente"
        messages.success(self.request, success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                print(field, error)
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/compras/")

    def get_success_url(self):
        return reverse_lazy("Compras")

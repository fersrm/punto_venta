from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect

# Permisos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# Modelos y formularios
from .forms import ProveedorAgregarForm, ProveedorEditarForm
from .models import Proveedor

# funciones
from utils.helpers import buscar_campos

# Create your views here.

# ---------------CRUD PROVEEDORES------------


class ProveedorListView(LoginRequiredMixin, PermitsPositionMixin, ListView):
    model = Proveedor
    template_name = "pages/proveedores/proveedor.html"
    paginate_by = 7

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar")
        campos_busqueda = ["run_proveedor", "nombre_proveedor", "correo_proveedor"]
        queryset = buscar_campos(self.model, campos_busqueda, busqueda)
        queryset = queryset.order_by("-id_proveedor")

        if not queryset and busqueda:
            messages.error(self.request, f"No existe {busqueda}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(context["object_list"], self.paginate_by)
        page = self.request.GET.get("page")
        context["object_list"] = paginator.get_page(page)
        return context


# -------------------------------------------------


class AgregarProveedorView(LoginRequiredMixin, PermitsPositionMixin, CreateView):
    model = Proveedor
    form_class = ProveedorAgregarForm
    template_name = "pages/proveedores/modal/AddProveedor.html"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Proveedor agregado correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/proveedores/")

    def get_success_url(self):
        return reverse_lazy("Proveedores")


# -------------------------------------------------


class EditarProveedorView(LoginRequiredMixin, PermitsPositionMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorEditarForm
    template_name = "pages/proveedores/modal/EditProveedor.html"

    def form_valid(self, form):
        form.clean()
        form.save()
        messages.success(self.request, "Proveedor editado correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/proveedores/")

    def get_success_url(self):
        return reverse_lazy("Proveedores")


# --------------------------------------------------


class EliminarProveedorView(LoginRequiredMixin, PermitsPositionMixin, DeleteView):
    model = Proveedor
    success_url = reverse_lazy("Proveedores")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        messages.success(self.request, "Proveedor eliminado correctamente")
        self.object.delete()
        return redirect(self.get_success_url())

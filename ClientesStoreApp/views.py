# Librerías de Django
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy

# Premiosos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# Modelos y formularios
from .forms import ClienteAgregarForm, ClienteEditarForm
from .models import Cliente

# funciones
from utils.helpers import buscar_campos

# Create your views here.

# ---------------CRUD CLIENTES------------


class CLienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "pages/clientes/clientes.html"
    paginate_by = 7

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar")
        campos_busqueda = [
            "run_cliente",
            "nombre_cliente",
            "apellido_cliente",
            "correo_cliente",
        ]
        queryset = buscar_campos(self.model, campos_busqueda, busqueda)
        queryset = queryset.order_by("-id_cliente")

        if not queryset and busqueda:
            messages.error(self.request, f"No Existe {busqueda}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(context["object_list"], self.paginate_by)
        page = self.request.GET.get("page")
        context["object_list"] = paginator.get_page(page)
        return context


# -------------------------------------------------


class AgregarClientesView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteAgregarForm
    template_name = "pages/clientes/modal/AddClient.html"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Cliente agregado correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                print(field, error)
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/clientes/")

    def get_success_url(self):
        return reverse_lazy("Clientes")


# -------------------------------------------------


class EditarCLientesView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteEditarForm
    template_name = "pages/clientes/modal/EditClient.html"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Cliente editado correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                print(field, error)
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/clientes/")

    def get_success_url(self):
        return reverse_lazy("Clientes")


# --------------------------------------------------


class EliminarClienteView(LoginRequiredMixin, PermitsPositionMixin, DeleteView):
    model = Cliente
    success_url = reverse_lazy("Clientes")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        messages.success(self.request, "Cliente eliminado correctamente")
        self.object.delete()
        return redirect(self.get_success_url())

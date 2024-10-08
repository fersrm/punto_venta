from django.views.generic import CreateView, ListView, View
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.db.models import Q

# Permisos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# Modelos y formularios
from .forms import PromocionesForm
from .models import Promociones, Producto

# Create your views here.


class AgregarPromocionesView(
    LoginRequiredMixin, PermitsPositionMixin, CreateView, ListView
):
    model = Promociones
    form_class = PromocionesForm
    template_name = "pages/promociones/promociones.html"

    def form_valid(self, form):
        form.save()
        success_message = "Promocion agregada correctamente"
        messages.success(self.request, success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error en el formulario")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return HttpResponseRedirect("/promociones/")

    def get_success_url(self):
        return reverse_lazy("Promociones")

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar", "").upper()
        queryset = self.model.objects.all()

        if busqueda == "ACTIVO":
            queryset = queryset.filter(activo=True)
        elif busqueda == "DESACTIVADO":
            queryset = queryset.filter(activo=False)
        elif busqueda:
            queryset = queryset.filter(
                Q(producto_FK__descripcion_producto__icontains=busqueda)
                | Q(producto_FK__codigo_producto__exact=busqueda)
            )

            if not queryset:
                messages.error(self.request, f"NO HAY PROMOCIÓN {busqueda}")

        return queryset.order_by("-id_promocion")


class ProductosPorCategoriaView(LoginRequiredMixin, PermitsPositionMixin, View):
    def get(self, request, *args, **kwargs):
        categoria_id = request.GET.get("categoria_id")

        if not categoria_id:
            productos = Producto.objects.all().values("pk", "descripcion_producto")
        else:
            productos = Producto.objects.filter(categoria_FK_id=categoria_id).values(
                "pk", "descripcion_producto"
            )

        productos_list = list(productos)
        return JsonResponse({"productos": productos_list}, safe=False)

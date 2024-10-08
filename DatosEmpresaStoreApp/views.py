from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View

# Permisos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# Modelos y formularios
from .forms import DatosEmpresaEditarContactoForm, DatosEmpresaEditarForm
from .models import DatosEmpresa

# Productos formulario
from ProductosStoreApp.forms import CategoriaAgregarForm

# --------------------SETTING---------------------


class EditarDatosEmpresaView(LoginRequiredMixin, PermitsPositionMixin, View):
    template_name = "pages/empresa/setting.html"

    def get(self, request, *args, **kwargs):
        empresa = get_object_or_404(DatosEmpresa, pk=1)
        form_empresa = DatosEmpresaEditarContactoForm(instance=empresa)
        form_empresa_impuesto = DatosEmpresaEditarForm(instance=empresa)
        form_categoria = CategoriaAgregarForm()

        return self.render_forms(
            request, form_empresa, form_empresa_impuesto, form_categoria, empresa
        )

    def post(self, request, *args, **kwargs):
        empresa = get_object_or_404(DatosEmpresa, pk=1)

        if "submit_form_empresa" in request.POST:
            form_empresa = DatosEmpresaEditarContactoForm(
                request.POST, request.FILES, instance=empresa
            )
            if form_empresa.is_valid():
                form_empresa.save()
                messages.success(request, "Datos del local actualizados correctamente")
                return redirect("Setting")
            form_empresa_impuesto = DatosEmpresaEditarForm(instance=empresa)
            form_categoria = CategoriaAgregarForm()

        elif "submit_form_categoria" in request.POST:
            form_categoria = CategoriaAgregarForm(request.POST)
            if form_categoria.is_valid():
                form_categoria.save()
                messages.success(request, "Categoría añadida correctamente")
                return redirect("Setting")
            form_empresa = DatosEmpresaEditarContactoForm(instance=empresa)
            form_empresa_impuesto = DatosEmpresaEditarForm(instance=empresa)

        elif "submit_form_impuesto" in request.POST:
            form_empresa_impuesto = DatosEmpresaEditarForm(
                request.POST, instance=empresa
            )
            if form_empresa_impuesto.is_valid():
                form_empresa_impuesto.save()
                messages.success(request, "Datos actualizados correctamente")
                return redirect("Setting")
            form_empresa = DatosEmpresaEditarContactoForm(instance=empresa)
            form_categoria = CategoriaAgregarForm()

        return self.render_forms(
            request, form_empresa, form_empresa_impuesto, form_categoria, empresa
        )

    def render_forms(
        self, request, form_empresa, form_empresa_impuesto, form_categoria, empresa
    ):
        return render(
            request,
            self.template_name,
            {
                "form_empresa": form_empresa,
                "empresa": empresa,
                "form_categoria": form_categoria,
                "form_impuesto": form_empresa_impuesto,
            },
        )

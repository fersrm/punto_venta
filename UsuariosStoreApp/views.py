from django.views.generic import ListView, DeleteView, View
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import update_session_auth_hash

# Permisos
from django.contrib.auth.mixins import LoginRequiredMixin
from ProyectoTaller.mixins import PermitsPositionMixin

# Modelos y formularios
from django.contrib.auth.models import User
from .forms import (
    ProfileUpdateForm,
    UsuarioAgregarForm,
    UsuarioEditarForm,
    ProfileCreateForm,
    CambiarContrasenaForm,
    UserUpdateForm,
)

# funciones
from utils.helpers import buscar_campos

# Create your views here.

# ---------------CRUD USUARIOS------------


class UsuarioListView(LoginRequiredMixin, PermitsPositionMixin, ListView):
    model = User
    template_name = "pages/usuarios/usuarios.html"
    paginate_by = 7

    def get_queryset(self):
        busqueda = self.request.GET.get("buscar")

        campos_busqueda = ["first_name", "last_name", "username", "email"]
        queryset = buscar_campos(self.model, campos_busqueda, busqueda)
        queryset = queryset.order_by("-id")

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


class AgregarUsuarioView(LoginRequiredMixin, PermitsPositionMixin, View):
    template_name = "pages/usuarios/modal/AddUser.html"

    def get(self, request, *args, **kwargs):
        user_form = UsuarioAgregarForm()
        profile_form = ProfileCreateForm()

        context = {"user_form": user_form, "profile_form": profile_form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UsuarioAgregarForm(request.POST)
        profile_form = ProfileCreateForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user_FK = user
            profile.save()
            messages.success(request, "Usuario creado con Éxito.")
            return redirect("Usuarios")

        context = {"user_form": user_form, "profile_form": profile_form}
        return render(request, self.template_name, context)


# -------------------------------------------------


class EditarUsuarioView(LoginRequiredMixin, PermitsPositionMixin, View):
    template_name = "pages/usuarios/modal/EditUser.html"

    def get(self, request, *args, **kwargs):
        # Obtener el usuario que se va a editar
        usuario = get_object_or_404(User, pk=kwargs["pk"])
        # Inicializar los formularios con los datos existentes
        usuario_form = UsuarioEditarForm(instance=usuario)
        profile_form = ProfileUpdateForm(instance=usuario.profile)
        context = {
            "usuario_form": usuario_form,
            "profile_form": profile_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Obtener el usuario que se va a editar
        usuario = get_object_or_404(User, pk=kwargs["pk"])
        # Cargar los formularios con los datos del request y las instancias existentes
        usuario_form = UsuarioEditarForm(request.POST, instance=usuario)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=usuario.profile
        )

        # Verificar si ambos formularios son válidos
        if usuario_form.is_valid() and profile_form.is_valid():
            if usuario.is_superuser:
                messages.error(request, "No puedes editar al usuario ADMIN.")
                return HttpResponseRedirect("/usuarios/")

            # Guardar los formularios
            usuario_form.save()
            profile_form.save()
            messages.success(request, "Usuario editado correctamente.")
            return HttpResponseRedirect(self.get_success_url())

        else:
            messages.error(request, "Error en el formulario")

            context = {
                "usuario_form": usuario_form,
                "profile_form": profile_form,
            }
            return render(request, self.template_name, context)

    def get_success_url(self):
        return reverse_lazy("Usuarios")


# --------------------------------------------------


class EliminarUsuarioView(LoginRequiredMixin, PermitsPositionMixin, DeleteView):
    model = User
    success_url = reverse_lazy("Usuarios")

    def get(self, request, *args, **kwargs):
        usuario = self.get_object()

        if usuario.is_superuser:
            messages.error(request, "No puedes eliminar al usuario ADMIN.")
            return redirect(self.success_url)

        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect(self.success_url)


############## PERFIL DE USUARIO #############
class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = "pages/perfil/perfil.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

        context = {"user_form": user_form, "profile_form": profile_form}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                print(profile_form.cleaned_data.get("image"))
                user_form.save()
                profile_form.save()
                messages.success(request, "Perfil actualizado con éxito.")
            except Exception as e:
                print(e)
                messages.error(request, "Error al guardar la imagen")

            return redirect("Profile")

        context = {"user_form": user_form, "profile_form": profile_form}

        return render(request, self.template_name, context)


class PasswordChangeView(LoginRequiredMixin, View):
    template_name = "pages/perfil/pass_change.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        form = CambiarContrasenaForm(user=user)

        context = {"form_pass": form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = request.user
        form = CambiarContrasenaForm(user=user, data=request.POST)

        if form.is_valid():
            form.save()
            update_session_auth_hash(
                self.request, self.request.user
            )  # Mantener la sesión activa después de cambiar la contraseña
            messages.success(request, "Perfil actualizado con éxito.")
            return redirect("CambioPass")

        context = {"form_pass": form}

        return render(request, self.template_name, context)

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Position, Profile
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import PasswordChangeForm

###########################
### terminar de revisar ###
###########################

# --------------------Usuario ----------


class BaseUsuarioForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nombre", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Apellido", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    username = forms.CharField(
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
        ]

    def clean_username(self):
        nombre_usuario = self.cleaned_data.get("username").upper()
        return nombre_usuario


class UsuarioEditarForm(BaseUsuarioForm):
    class Meta(BaseUsuarioForm.Meta):
        fields = BaseUsuarioForm.Meta.fields


class UsuarioAgregarForm(UserCreationForm, BaseUsuarioForm):
    password1 = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    password2 = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta(BaseUsuarioForm.Meta):
        fields = BaseUsuarioForm.Meta.fields + ["password1", "password2"]

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        validate_password(password1)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")

        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(
        label="Imagen",
        widget=forms.FileInput(attrs={"class": "form-control"}),
        required=False,
    )
    telefono_user = forms.CharField(
        label="Teléfono", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Profile
        fields = ["image", "telefono_user"]

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "El tamaño del archivo de imagen no debe exceder los 5 MB."
            )
        return image


class ProfileCreateForm(ProfileUpdateForm):
    position_FK = forms.ModelChoiceField(
        label="Cargo",
        queryset=Position.objects.exclude(pk=1),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta(ProfileUpdateForm.Meta):
        fields = ProfileUpdateForm.Meta.fields + ["position_FK"]


## PARA PERFIL DE USUARIO ##
class UserUpdateForm(forms.ModelForm):

    username = forms.CharField(
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    email = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    first_name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]


class CambiarContrasenaForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("old_password")  # Elimina el campo old_password

    new_password1 = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    new_password2 = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["new_password1", "new_password2"]

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get("new_password1")
        validate_password(new_password1)
        return new_password1

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("Passwords do not match")

        return cleaned_data

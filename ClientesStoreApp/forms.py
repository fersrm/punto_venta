from django import forms
from .models import Cliente
import re

# --------------------Tabla Usuario ----------


class BaseClienteForm(forms.ModelForm):
    run_cliente = forms.CharField(
        label="Run", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    nombre_cliente = forms.CharField(
        label="Nombre", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    apellido_cliente = forms.CharField(
        label="Apellido", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    correo_cliente = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    telefono_cliente = forms.CharField(
        label="Teléfono", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    direccion = forms.CharField(
        label="Dirección", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Cliente
        fields = [
            "run_cliente",
            "nombre_cliente",
            "apellido_cliente",
            "correo_cliente",
            "telefono_cliente",
            "direccion",
        ]

    def clean_run_cliente(self):
        rut_regex = re.compile(r"^\d{1,8}-[\dkK]$")
        run_cliente = self.cleaned_data.get("run_cliente").upper()
        if not rut_regex.match(run_cliente):
            raise forms.ValidationError("El formato del RUT no es válido.")
        return run_cliente

    def clean_nombre_cliente(self):
        nombre_cliente = self.cleaned_data.get("nombre_cliente").capitalize()
        if not nombre_cliente.isalpha():
            raise forms.ValidationError("El nombre solo puede contener letras.")
        return nombre_cliente

    def clean_apellido_cliente(self):
        apellido_cliente = self.cleaned_data.get("apellido_cliente").capitalize()
        if not apellido_cliente.isalpha():
            raise forms.ValidationError("El apellido solo puede contener letras.")
        return apellido_cliente

    def clean_email_cliente(self):
        email_cliente = self.cleaned_data.get("email_cliente")
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.match(email_cliente):
            raise forms.ValidationError(
                "El formato del correo electrónico no es válido."
            )
        return email_cliente

    def clean_telefono_cliente(self):
        telefono_cliente = self.cleaned_data.get("telefono_cliente")
        telefono_regex = re.compile(r"^\+56(\d{9})$")
        if not telefono_regex.match(telefono_cliente):
            raise forms.ValidationError(
                "El formato del teléfono no es válido. Debe ser +569 seguido de 8 dígitos."
            )
        return telefono_cliente


class ClienteEditarForm(BaseClienteForm):
    class Meta(BaseClienteForm.Meta):
        fields = BaseClienteForm.Meta.fields


class ClienteAgregarForm(BaseClienteForm):
    class Meta(BaseClienteForm.Meta):
        fields = BaseClienteForm.Meta.fields

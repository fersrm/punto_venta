from django import forms
from .models import Proveedor, Giro, Rubro
import re


class BaseProveedorForm(forms.ModelForm):
    run_proveedor = forms.CharField(
        label="RUT", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    nombre_proveedor = forms.CharField(
        label="Nombre Empresa", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    razon_social = forms.CharField(
        label="Razón social", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    correo_proveedor = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    telefono_proveedor = forms.CharField(
        label="Teléfono", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    direccion = forms.CharField(
        label="Dirección", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    contacto = forms.CharField(
        label="Contacto", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    giro_FK = forms.ModelChoiceField(
        label="Giro",
        queryset=Giro.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    rubro_FK = forms.ModelChoiceField(
        label="Categoría",
        queryset=Rubro.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Proveedor
        fields = [
            "run_proveedor",
            "nombre_proveedor",
            "razon_social",
            "correo_proveedor",
            "telefono_proveedor",
            "contacto",
            "direccion",
            "giro_FK",
            "rubro_FK",
        ]

    def clean_run_proveedor(self):
        rut_regex = re.compile(r"^\d{1,8}-[\dkK]$")
        run_proveedor = self.cleaned_data.get("run_proveedor").upper()
        if not rut_regex.match(run_proveedor):
            raise forms.ValidationError("El formato del RUT no es válido.")
        return run_proveedor


class ProveedorEditarForm(BaseProveedorForm):
    class Meta(BaseProveedorForm.Meta):
        fields = BaseProveedorForm.Meta.fields


class ProveedorAgregarForm(BaseProveedorForm):
    class Meta(BaseProveedorForm.Meta):
        fields = BaseProveedorForm.Meta.fields

from django import forms
from .models import DatosEmpresa
import re

# -------------------DatosEmpresa----------------


class DatosEmpresaEditarContactoForm(forms.ModelForm):
    telefono = forms.CharField(
        label="Teléfono", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    image = forms.ImageField(
        label="Imagen",
        widget=forms.FileInput(attrs={"class": "form-control"}),
        required=False,
    )

    class Meta:
        model = DatosEmpresa
        fields = ["telefono", "email", "image"]

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "El tamaño del archivo de imagen no debe exceder los 5 MB."
            )
        return image

    def clean_telefono(self):
        telefono_cliente = self.cleaned_data.get("telefono_cliente")
        telefono_regex = re.compile(r"^\+56(\d{9})$")
        if not telefono_regex.match(telefono_cliente):
            raise forms.ValidationError(
                "El formato del teléfono no es válido. Debe ser +569 seguido de 8 dígitos."
            )
        return telefono_cliente


class DatosEmpresaEditarForm(forms.ModelForm):
    IVA = forms.IntegerField(
        label="IVA %",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    margen_global = forms.DecimalField(
        label="Margen Global %",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = DatosEmpresa
        fields = ["IVA", "margen_global"]

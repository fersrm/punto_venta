from django import forms
from .models import Ventas

# -------------------DatosEmpresa----------------


class VentasForm(forms.ModelForm):
    carrito = forms.CharField(
        label="Carrito",
        widget=forms.TextInput(
            attrs={"class": "visually-hidden", "id": "carrito-input"}
        ),
        required=False,
    )

    class Meta:
        model = Ventas
        fields = ["carrito"]

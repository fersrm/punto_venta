from django import forms
from VentasStoreApp.models import Ventas

# -------------------DatosEmpresa----------------


class VentasFacturasForm(forms.ModelForm):
    carrito = forms.CharField(
        label="Carrito",
        widget=forms.TextInput(
            attrs={"class": "visually-hidden", "id": "carrito-input"}
        ),
    )
    cliente_id = forms.IntegerField(
        label="ID Cliente",
        widget=forms.TextInput(attrs={"class": "visually-hidden", "id": "id_cliente"}),
    )

    class Meta:
        model = Ventas
        fields = ["carrito", "cliente_id"]

from django import forms
from .models import Compras, Proveedor
from .choices import TIPO_DOCUMENTO, TIPO_IMPUESTO

# --------------------Tabla Usuario ----------


class BaseComprasForm(forms.ModelForm):
    num_documento = forms.CharField(
        label="Número de Documento",
        widget=forms.TextInput(attrs={"class": "form-control", "id": "num_documento"}),
    )
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={"class": "form-control", "id": "fecha"}),
    )
    total = forms.IntegerField(
        label="Total",
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "total"}),
    )
    tipo_documento = forms.ChoiceField(
        label="Tipo de Documento",
        choices=TIPO_DOCUMENTO,
        widget=forms.Select(attrs={"class": "form-select", "id": "tipo_documento"}),
    )
    tipo_impuesto = forms.ChoiceField(
        label="Con/Sin Impuesto",
        choices=TIPO_IMPUESTO,
        widget=forms.Select(attrs={"class": "form-select", "id": "tipo_impuesto"}),
    )
    proveedor_FK = forms.ModelChoiceField(
        label="Proveedor",
        queryset=Proveedor.objects.all(),
        widget=forms.Select(attrs={"class": "form-select", "id": "proveedor"}),
    )

    class Meta:
        model = Compras
        fields = [
            "num_documento",
            "fecha",
            "total",
            "tipo_documento",
            "tipo_impuesto",
            "proveedor_FK",
        ]

    def clean_num_documento(self):
        num_documento = self.cleaned_data.get("num_documento").upper()
        return num_documento


class ComprasAgregarForm(BaseComprasForm):
    class Meta(BaseComprasForm.Meta):
        fields = BaseComprasForm.Meta.fields

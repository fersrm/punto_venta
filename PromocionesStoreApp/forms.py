from datetime import datetime, timedelta
from django import forms
from .models import Promociones, Producto
from ProductosStoreApp.models import Categoria


class PromocionesForm(forms.ModelForm):
    fecha_inicio = forms.DateField(
        label="Fecha de Inicio",
        widget=forms.DateInput(attrs={"class": "form-control"}),
    )

    fecha_termino = forms.DateField(
        label="Fecha de Termino ",
        widget=forms.DateInput(attrs={"class": "form-control"}),
    )

    descuento = forms.IntegerField(
        label="Descuento %",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    producto_FK = forms.ModelChoiceField(
        label="Producto",
        queryset=Producto.objects.all(),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_producto_FK"}),
    )

    categoria_FK = forms.ModelChoiceField(
        label="Categoría",
        queryset=Categoria.objects.all(),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_categoria_FK"}),
    )

    class Meta:
        model = Promociones
        fields = [
            "fecha_inicio",
            "fecha_termino",
            "descuento",
            "producto_FK",
            "categoria_FK",
        ]

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_termino = cleaned_data.get("fecha_termino")
        descuento = cleaned_data.get("descuento")
        producto = cleaned_data.get("producto_FK")

        if fecha_inicio and fecha_termino:
            if descuento is None or descuento < 1:
                raise forms.ValidationError("Descuento debe ser mayor 1")

            try:
                fecha_inicio = datetime.strptime(str(fecha_inicio), "%Y-%m-%d")
                fecha_termino = datetime.strptime(str(fecha_termino), "%Y-%m-%d")
            except ValueError:
                raise forms.ValidationError("formato de fecha invalido")

            if fecha_inicio < datetime.now() - timedelta(days=1):
                raise forms.ValidationError(
                    "La fecha de inicio debe ser igual o mayor que la fecha actual"
                )

            if fecha_inicio >= fecha_termino:
                raise forms.ValidationError(
                    "la fecha de inicio debe ser menor a la fecha de termino"
                )

            # --------------------------------------------------------------------

            existe_producto = Promociones.objects.filter(
                producto_FK=producto,
                fecha_termino__gte=fecha_inicio,
                fecha_inicio__lte=fecha_termino,
                activo=True,
            ).exclude(id_promocion=self.instance.id_promocion)

            if existe_producto.exists():
                raise forms.ValidationError(
                    "Este producto ya tiene una promoción activa."
                )

        return cleaned_data

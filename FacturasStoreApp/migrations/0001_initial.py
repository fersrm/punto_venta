# Generated by Django 4.2.6 on 2024-10-08 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("ClientesStoreApp", "0001_initial"),
        ("VentasStoreApp", "0001_initial"),
        ("ProductosStoreApp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Facturas",
            fields=[
                ("id_factura", models.AutoField(primary_key=True, serialize=False)),
                ("total_factura", models.IntegerField()),
                ("total_descuento", models.IntegerField(default=0)),
                (
                    "cliente_fk",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="ClientesStoreApp.cliente",
                    ),
                ),
                (
                    "venta_FK",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="VentasStoreApp.ventas",
                    ),
                ),
            ],
            options={
                "db_table": "facturas",
            },
        ),
        migrations.CreateModel(
            name="DetalleFacturas",
            fields=[
                (
                    "id_detalle_factura",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("cantidad", models.IntegerField()),
                ("total", models.IntegerField()),
                ("producto_nombre", models.CharField(max_length=255)),
                ("producto_precio", models.IntegerField()),
                (
                    "factura_FK",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="FacturasStoreApp.facturas",
                    ),
                ),
                (
                    "producto_FK",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="ProductosStoreApp.producto",
                    ),
                ),
            ],
            options={
                "db_table": "detallefactura",
            },
        ),
    ]

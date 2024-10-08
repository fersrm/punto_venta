# Generated by Django 4.2.6 on 2024-10-08 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cliente",
            fields=[
                ("id_cliente", models.AutoField(primary_key=True, serialize=False)),
                ("run_cliente", models.CharField(max_length=15, unique=True)),
                ("nombre_cliente", models.CharField(max_length=45)),
                ("apellido_cliente", models.CharField(max_length=45)),
                ("correo_cliente", models.EmailField(max_length=64, unique=True)),
                ("telefono_cliente", models.CharField(max_length=15)),
                ("direccion", models.CharField(max_length=45)),
            ],
            options={
                "db_table": "cliente",
            },
        ),
    ]

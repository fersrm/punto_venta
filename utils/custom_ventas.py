from decimal import Decimal
from ProductosStoreApp.models import Producto
from PromocionesStoreApp.models import Promociones
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Subquery, IntegerField, Value, OuterRef
from django.db.models.functions import Coalesce

# --------------Calculo de ventas ---------------------


def carrito_json(carrito_str):
    import json

    try:
        carrito_list = json.loads(carrito_str)

        if isinstance(carrito_list, list):
            return carrito_list
        else:
            return []
    except json.JSONDecodeError:
        return []


def verificar_stock_y_calcular_total(carrito):
    total = 0
    total_descuento = 0

    for item in carrito:
        producto = get_object_or_404(Producto, id_producto=item["id"])
        cantidad = item["cantidad"]

        # Obtener precio y medida del producto
        precio = producto.precio_venta
        medida = producto.tipo_medida

        # Verificar stock disponible
        if medida == "UNIDAD":
            try:
                cantidad = int(cantidad)
            except ValueError:
                raise ValueError(f"La cantidad {cantidad} no es un número válido.")

            if producto.stock < cantidad:
                raise ValueError(
                    f"No hay suficiente stock para el producto {producto.descripcion_producto}"
                )
            total_producto = cantidad * precio
        else:
            cantidad_kilos = cantidad / 1000
            if producto.stock < cantidad_kilos:
                raise ValueError(
                    f"No hay suficiente stock para el producto {producto.descripcion_producto}"
                )
            total_producto = round(cantidad_kilos * precio)

        # Calcular descuento si existe una promoción activa
        now = timezone.now().date()

        producto_con_descuento = (
            Producto.objects.filter(id_producto=producto.id_producto)
            .annotate(
                descuento_producto=Coalesce(
                    Subquery(
                        Promociones.objects.filter(
                            producto_FK=OuterRef("id_producto"),
                            activo=True,
                            fecha_termino__gte=now,
                        )
                        .order_by("fecha_inicio")
                        .values("descuento")[:1]
                    ),
                    Value(0),
                    output_field=IntegerField(),
                )
            )
            .first()
        )

        # Aplicar el descuento al producto
        descuento_aplicado = total_producto * (
            producto_con_descuento.descuento_producto / 100
        )
        total_producto -= descuento_aplicado

        # Sumar al total acumulado
        total += total_producto
        total_descuento += descuento_aplicado

    return total, total_descuento


def procesar_carrito(carrito, documento, detalle_modelo, detalle_fk):
    for item in carrito:
        producto = get_object_or_404(Producto, id_producto=item["id"])
        cantidad = item["cantidad"]

        # Obtener precio y medida del producto
        precio = producto.precio_venta
        medida = producto.tipo_medida

        # Calcular el total basado en la cantidad y medida
        if medida == "UNIDAD":
            total = cantidad * precio
        else:
            cantidad_kilos = cantidad / 1000
            total = round(cantidad_kilos * precio)

        # Crear el detalle del documento (boleta o factura)
        detalle = detalle_modelo(
            cantidad=cantidad,
            total=total,
            producto_FK=producto,
            producto_nombre=producto.descripcion_producto,
            producto_precio=producto.precio_venta,
            **{detalle_fk: documento},
        )
        detalle.save()

        # Actualizar stock del producto
        if medida == "UNIDAD":
            producto.stock -= Decimal(cantidad)
        else:
            producto.stock -= Decimal(cantidad) / Decimal(1000)

        producto.save()

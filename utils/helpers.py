from django.utils import timezone
from django.db.models import Q, Sum
from datetime import timedelta, datetime


def buscar_campos(model, campos, busqueda):
    modelo = model.objects.all()
    queries = []
    if busqueda:
        queries = [Q(**{campo + "__icontains": busqueda}) for campo in campos]
    if queries:
        query = queries.pop()
        for item in queries:
            query |= item
        modelo = modelo.filter(query).distinct()
    return modelo


def buscar_fecha(model, busqueda_fecha):
    modelo = model.objects.all()
    query = Q(venta_FK__fecha_emision__icontains=busqueda_fecha)
    modelo = modelo.filter(query).distinct()
    return modelo


def buscar_venta(model, campos, busqueda):
    modelo = model.objects.all()
    queries = []
    if busqueda is not None and busqueda.isdigit():
        busqueda = int(busqueda)
        for campo in campos:
            queries.append(Q(**{campo: busqueda}))
    elif busqueda:
        queries.append(Q(**{"venta_FK__usuario_FK__username": busqueda}))
    if queries:
        query = queries.pop()
        for item in queries:
            query |= item
        modelo = modelo.filter(query).distinct()
    return modelo


def total_dia(model, count_field, sum_field):
    today = timezone.now().date()  # fecha actual
    query = Q(venta_FK__fecha_emision__icontains=today)
    objects = model.objects.filter(query).distinct()
    count = objects.count()
    total = objects.aggregate(total=Sum(sum_field))["total"]
    return {count_field: count, sum_field: total if total is not None else 0}


def generar_rango_fechas(periodo, now):
    """Genera el rango de fechas basado en el periodo."""
    if periodo == "dia":
        return [now - timedelta(days=i) for i in range(6, -1, -1)]
    elif periodo == "semana":
        return [now - timedelta(weeks=i) for i in range(6, -1, -1)]
    elif periodo == "mes":
        return [now - timedelta(days=30 * i) for i in range(6, -1, -1)]
    else:
        raise ValueError("El periodo debe ser 'dia', 'semana' o 'mes'")


def calcular_ventas_y_facturas(boleta, factura, query_ventas):
    """Calcula las ventas de boletas y facturas en un rango de tiempo."""
    objects_boletas = boleta.objects.filter(query_ventas).distinct()
    total_boletas = objects_boletas.aggregate(total=Sum("total_boleta"))["total"] or 0

    total_venta = total_boletas
    if factura:
        objects_facturas = factura.objects.filter(query_ventas).distinct()
        total_factura = (
            objects_facturas.aggregate(total=Sum("total_factura"))["total"] or 0
        )
        total_venta += total_factura

    return total_venta


def calcular_compras(compras, query_compras):
    """Calcula las compras en un rango de tiempo."""
    objects_compras = compras.objects.filter(query_compras).distinct()
    total_compras = objects_compras.aggregate(total=Sum("total"))["total"] or 0
    return total_compras


def total_ventas(boleta, compras, periodo="semana", factura=None):
    ventas_totales = {}
    compras_totales = []
    # Obtener la fecha actual
    now = timezone.localtime(timezone.now())
    # Crear un arreglo de fechas
    date_range = generar_rango_fechas(periodo, now)
    # Calcular el total de ventas para cada día en el rango
    for date in date_range:
        if periodo == "dia":
            # Filtrar Boletas por el rango de fecha del día
            first_day = timezone.make_aware(
                timezone.datetime(date.year, date.month, date.day, 0, 0, 0)
            )
            last_day = timezone.make_aware(
                timezone.datetime(date.year, date.month, date.day, 23, 59, 59, 999999)
            )

        elif periodo == "semana":
            # Calcular el primer día (hace 7 días) y el último día (hoy)
            first_day = date - timedelta(weeks=1)
            last_day = date

        elif periodo == "mes":
            # Calcular el primer día y el último día del mes
            first_day = date.replace(day=1)
            if first_day.month == 12:
                last_day = first_day.replace(
                    year=first_day.year + 1, month=1, day=1
                ) - timedelta(days=1)
            else:
                last_day = first_day.replace(
                    month=first_day.month + 1, day=1
                ) - timedelta(days=1)

        # Crear las consultas para ventas y compras
        query_ventas = Q(venta_FK__fecha_emision__range=(first_day, last_day))
        query_compras = Q(fecha__range=(first_day, last_day))
        # Calcular ventas
        total_venta = calcular_ventas_y_facturas(boleta, factura, query_ventas)
        ventas_totales[date.strftime("%d-%m-%Y")] = total_venta
        # Calcular compras
        total_compras = calcular_compras(compras, query_compras)
        compras_totales.append(total_compras)

    return ventas_totales, compras_totales


def top_productos(
    model_productos, model_detalle, campos_producto, model_detalle_factura=None
):
    # Calcular la fecha de hace 30 días desde la fecha actual
    fecha_hace_30_dias = timezone.localtime(timezone.now()) - timedelta(days=30)

    # Obtener todos los productos
    productos_no_en_boletas = model_productos.objects.filter(
        detalleboletas__isnull=True, tipo_medida="UNIDAD"
    ).values(*campos_producto)

    # Agrega el prefijo 'producto_FK__' a cada campo en la lista campos_producto
    campos_producto_con_prefijo = ["producto_FK__" + campo for campo in campos_producto]

    # Obtener los productos más vendidos de DetalleBoletas
    productos_boletas = model_detalle.objects.filter(
        boleta_FK__venta_FK__fecha_emision__gte=fecha_hace_30_dias,
        producto_FK__tipo_medida="UNIDAD",
    ).values(*campos_producto_con_prefijo)

    productos_boletas = productos_boletas.annotate(total_vendido=Sum("cantidad"))

    # Unir los resultados de ambas consultas utilizando un left join y ordenar
    top_mas_vendidos_boleta = productos_boletas.order_by("-total_vendido")[:10]

    top_menos_vendidos_boleta = productos_boletas.order_by("total_vendido")[:10]

    # Convierte las consultas en listas
    productos_no_en_boletas_lista = list(productos_no_en_boletas)
    top_menos_vendidos_boleta_lista = list(top_menos_vendidos_boleta)
    top_mas_vendidos_boleta_lista = list(top_mas_vendidos_boleta)

    # ------------------------------------------------

    if model_detalle_factura:
        productos_no_en_ventas = model_productos.objects.filter(
            detalleboletas__isnull=True,
            detallefacturas__isnull=True,
            tipo_medida="UNIDAD",
        ).values(*campos_producto)

        # Obtener los productos más vendidos de DetalleBoletas
        productos_factura = model_detalle_factura.objects.filter(
            factura_FK__venta_FK__fecha_emision__gte=fecha_hace_30_dias,
            producto_FK__tipo_medida="UNIDAD",
        ).values(*campos_producto_con_prefijo)

        productos_factura = productos_factura.annotate(total_vendido=Sum("cantidad"))

        # Unir los resultados de ambas consultas utilizando un left join y ordenar
        top_mas_vendidos_factura = productos_factura.order_by("-total_vendido")[:10]
        top_menos_vendidos_factura = productos_factura.order_by("total_vendido")[:10]

        productos_no_en_ventas_lista = list(productos_no_en_ventas)
        top_menos_vendidos_factura_lista = list(top_menos_vendidos_factura)
        top_mas_vendidos_factura_lista = list(top_mas_vendidos_factura)

        # Combina las listas
        productos_combinados_top_menos = (
            top_menos_vendidos_boleta_lista + top_menos_vendidos_factura_lista
        )

        productos_combinados_top_mas = (
            top_mas_vendidos_boleta_lista + top_mas_vendidos_factura_lista
        )

        # Agrupa los productos
        result_top_menos = agrupar_busqueda(productos_combinados_top_menos)

        result_top_mas = agrupar_busqueda(productos_combinados_top_mas)

        # Ordena las listas
        result_top_menos = sorted(result_top_menos, key=lambda x: x["total_vendido"])

        result_top_menos = productos_no_en_ventas_lista + result_top_menos

        result_top_mas = sorted(
            result_top_mas,
            key=lambda x: x["total_vendido"],
            reverse=True,
        )

        # Seleccionar los primeros 10 elementos de cada lista
        top_menos_vendidos = result_top_menos[:10]
        top_mas_vendidos = result_top_mas[:10]

    else:
        productos_combinados_top_menos = (
            productos_no_en_boletas_lista + top_menos_vendidos_boleta_lista
        )
        # Toma los primeros 10 elementos de la lista combinada
        top_menos_vendidos = productos_combinados_top_menos[:10]
        top_mas_vendidos = top_mas_vendidos_boleta

    return top_mas_vendidos, top_menos_vendidos


def agrupar_busqueda(data):
    from collections import defaultdict

    combined_data = defaultdict(lambda: {"total_vendido": 0})

    for entry in data:
        codigo_producto = entry["producto_FK__codigo_producto"]
        combined_data[codigo_producto]["producto_FK__codigo_producto"] = codigo_producto
        combined_data[codigo_producto]["producto_FK__descripcion_producto"] = entry[
            "producto_FK__descripcion_producto"
        ]
        combined_data[codigo_producto][
            "producto_FK__categoria_FK__nombre_categoria"
        ] = entry["producto_FK__categoria_FK__nombre_categoria"]
        combined_data[codigo_producto]["producto_FK__stock"] = entry[
            "producto_FK__stock"
        ]
        combined_data[codigo_producto]["producto_FK__precio_venta"] = entry[
            "producto_FK__precio_venta"
        ]
        combined_data[codigo_producto]["total_vendido"] += entry["total_vendido"]

    result = list(combined_data.values())
    return result


def generar_rango(fecha1, fecha2):
    """Genera el rango de fechas basándose en dos fechas proporcionadas."""
    if fecha1 and fecha2:
        fecha_inicio = datetime.strptime(fecha1, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha2, "%Y-%m-%d")
    else:
        fecha_inicio = timezone.localtime(timezone.now())
        fecha_fin = timezone.localtime(timezone.now())

    # Verifica que la fecha de inicio sea menor o igual a la fecha de fin
    if fecha_inicio > fecha_fin:
        fecha_inicio = timezone.localtime(timezone.now())
        fecha_fin = timezone.localtime(timezone.now())

    # Genera el rango de fechas desde fecha_fin hasta fecha_inicio
    return [
        fecha_fin - timedelta(days=i)
        for i in range((fecha_fin - fecha_inicio).days + 1)
    ]


def calcular_ventas_dia(boleta, factura, date):
    """Calcula las ventas totales (boletas y facturas) para un día específico."""
    # Filtrar Boletas por el rango de fecha del día
    start_time = timezone.make_aware(
        timezone.datetime(date.year, date.month, date.day, 0, 0, 0)
    )
    end_time = timezone.make_aware(
        timezone.datetime(date.year, date.month, date.day, 23, 59, 59, 999999)
    )

    query_ventas = Q(venta_FK__fecha_emision__range=(start_time, end_time))

    # Calcular total de boletas
    objects_boletas = boleta.objects.filter(query_ventas).distinct()
    total_boletas = objects_boletas.aggregate(total=Sum("total_boleta"))["total"] or 0

    # Calcular total de facturas (si aplica)
    total_venta = total_boletas
    if factura:
        objects_facturas = factura.objects.filter(query_ventas).distinct()
        total_factura = (
            objects_facturas.aggregate(total=Sum("total_factura"))["total"] or 0
        )
        total_venta += total_factura

    return total_venta


def buscar_fecha_rango(boleta, fecha1, fecha2, factura=None):
    ventas_totales = {}

    # Generar el rango de fechas
    date_range = generar_rango(fecha1, fecha2)

    # Calcular el total de ventas para cada día en el rango
    for date in date_range:
        total_venta = calcular_ventas_dia(boleta, factura, date)

        if total_venta != 0:
            ventas_totales[date.strftime("%d-%m-%Y")] = total_venta

    return ventas_totales

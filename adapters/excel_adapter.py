from ProductosStoreApp.models import Categoria


class ExcelAdapter:
    def __init__(self, row):
        self.row = row

    def get_codigo_producto(self):
        return str(self.row["código"]).strip().upper()

    def get_nombre_producto(self):
        return str(self.row["nombre"]).strip().upper()

    def get_categoria_producto(self):
        categoria = str(self.row["categoria"]).strip().upper()
        if not Categoria.objects.filter(nombre_categoria=categoria).exists():
            raise ValueError(f"La categoría '{categoria}' no existe.")
        return categoria

    def get_precio_proveedor(self):
        precio_proveedor = self.row["precio proveedor"]
        if not isinstance(precio_proveedor, int):
            raise ValueError("El precio del proveedor debe ser un número entero.")
        return precio_proveedor

    def get_precio_venta(self):
        precio_venta = self.row["precio venta"]
        if not isinstance(precio_venta, int):
            raise ValueError("El precio de venta debe ser un número entero.")
        return precio_venta

    def get_stock(self):
        stock = self.row["stock"]
        tipo_medida = self.get_tipo_medida()

        if tipo_medida == "UNIDAD" and not isinstance(stock, int):
            raise ValueError(
                "El stock debe ser un número entero cuando el tipo de medida es 'UNIDAD'."
            )

        if not isinstance(stock, (int, float)):
            raise ValueError("El stock debe ser un número.")

        return float(stock)

    def get_tipo_medida(self):
        tipo_medida = str(self.row["tipo medida"]).strip().upper()
        if tipo_medida not in ["UNIDAD", "KILO"]:
            raise ValueError("El tipo de medida debe ser 'UNIDAD' o 'KILO'.")
        return tipo_medida

    def get_tipo_impuesto(self):
        tipo_impuesto = str(self.row["tipo impuesto"]).strip().upper()
        if tipo_impuesto not in ["IVA", "EXENTO"]:
            raise ValueError("El tipo de impuesto debe ser 'IVA' o 'EXENTO'.")
        return tipo_impuesto

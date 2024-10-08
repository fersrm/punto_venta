class ExcelAdapter:
    def __init__(self, row):
        self.row = row

    def get_codigo_producto(self):
        return str(self.row["código"]).strip().upper()

    def get_nombre_producto(self):
        return str(self.row["nombre"]).strip().upper()

    def get_categoria_producto(self):
        return str(self.row["categoria"]).strip().upper()

    def get_precio_proveedor(self):
        return int(self.row["precio proveedor"])

    def get_precio_venta(self):
        return int(self.row["precio venta"])

    def get_margen_ganancia(self):
        return float(self.row["margen ganancia"])

    def get_stock(self):
        return float(self.row["stock"])

    def get_tipo_medida(self):
        return str(self.row["tipo media"]).strip().upper()

    def get_tipo_impuesto(self):
        return str(self.row["tipo impuesto"]).strip().upper()

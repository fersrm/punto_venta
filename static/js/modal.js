const $ = jQuery.noConflict();

// para productos
function abrir_modal_add(url) {
  $("#addModal").load(url, function () {
    $(this).modal("show");
    inicializarModal("myFormAdd");
    cargarDatos();
  });
}

// para productos en lotes
function abrir_modal_add_excel(url) {
  $("#addModalExcel").load(url, function () {
    $(this).modal("show");
  });
}

function abrir_modal_edit(url) {
  $("#editModal").load(url, function () {
    $(this).modal("show");
    inicializarModal("myFormEdit");
  });
}

function abrir_modal_plus(url) {
  $("#addProducModal").load(url, function () {
    $(this).modal("show");
    inicializarModal("myFormPlus");
  });
}

// para usuarios
function abrir_modal_add_user(url) {
  $("#addModalUser").load(url, function () {
    $(this).modal("show");
  });
}

function abrir_modal_edit_user(url) {
  $("#editModalUser").load(url, function () {
    $(this).modal("show");
  });
}

// tabla de stock
function tabla_poco_stock(url) {
  $("#tablaStock").load(url, function () {
    $(this).modal("show");
  });
}

// para clientes
function abrir_modal_add_client(url) {
  $("#addModalClient").load(url, function () {
    $(this).modal("show");
  });
}

function abrir_modal_edit_client(url) {
  $("#editModalClient").load(url, function () {
    $(this).modal("show");
  });
}

// para Proveedores
function abrir_modal_add_proveedor(url) {
  $("#addModalProveedor").load(url, function () {
    $(this).modal("show");
  });
}

function abrir_modal_edit_proveedor(url) {
  $("#editModalProveedor").load(url, function () {
    $(this).modal("show");
  });
}
//--------------------Variables de margenes---------------------

function inicializarModal(formId) {
  const precioBruto = document.querySelector(
    `#${formId} [name='precio_bruto_producto']`
  );
  const precioVenta = document.querySelector(
    `#${formId} [name='precio_venta']`
  );
  const margenGanancia = document.querySelector(
    `#${formId} [name='margen_ganancia']`
  );

  const tipoImpuesto = document.querySelector(
    `#${formId} [name='tipo_impuesto']`
  );

  function calcularYActualizarMargen() {
    const precioBrutoValor = parseFloat(precioBruto.value.trim());
    const precioVentaValor = parseFloat(precioVenta.value.trim());

    // Determinar el IVA según el tipo de impuesto
    let IVA = 0;
    if (tipoImpuesto.value === "IVA") {
      IVA = 0.19;
      if (typeof IVAEMPRESA === "number" && IVAEMPRESA > 0) {
        IVA = IVAEMPRESA;
      }
    }

    if (!isNaN(precioBrutoValor) && !isNaN(precioVentaValor)) {
      const costoConIva = precioBrutoValor * (1 + IVA);
      const margen = ((precioVentaValor - costoConIva) / costoConIva) * 100;
      margenGanancia.value = margen.toFixed(2);
    } else {
      margenGanancia.value = 0;
    }
  }
  // Agregar eventos a los inputs relevantes
  precioBruto.addEventListener("input", calcularYActualizarMargen);
  precioVenta.addEventListener("input", calcularYActualizarMargen);
  tipoImpuesto.addEventListener("change", calcularYActualizarMargen);

  // Calcular el margen al inicializar el formulario
  calcularYActualizarMargen();
}

//--------------Carga Datos de Productos-------------

function cargarDatos() {
  const codigoProductoInput = document.getElementById("id_codigo_producto");
  const form = document.getElementById("myFormAdd");

  codigoProductoInput.addEventListener("change", function () {
    const codigoProducto = codigoProductoInput.value;

    // Realiza una solicitud para cargar el archivo JSON
    fetch("/static/js/productos.json")
      .then((response) => response.json())
      .then((data) => {
        const productoEncontrado = data.find(
          (producto) => producto.codigo_producto === codigoProducto
        );

        if (productoEncontrado) {
          form.descripcion_producto.value =
            productoEncontrado.descripcion_producto;
          form.categoria_FK.value = productoEncontrado.categoria_FK;
          form.precio_bruto_producto.value =
            productoEncontrado.precio_bruto_producto;
          form.precio_venta.value = productoEncontrado.precio_venta;
          form.margen_ganancia.value = (
            ((productoEncontrado.precio_venta -
              productoEncontrado.precio_bruto_producto) /
              productoEncontrado.precio_bruto_producto) *
            100
          ).toFixed(2);
          //form.stock.value = productoEncontrado.stock;
          form.tipo_medida.value = productoEncontrado.tipo_medida;
          form.tipo_impuesto.value = productoEncontrado.tipo_impuesto;
        }
      })
      .catch((error) =>
        console.error("Error al cargar el archivo JSON:", error)
      );
  });
}

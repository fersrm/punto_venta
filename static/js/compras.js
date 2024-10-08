// CARGAR TABLA CON DATOS DEL LOCALSTORAGE, CALCULA LOS VALORES Y SE GUARDAN DATOS DEL FORMULARIO

document.addEventListener("DOMContentLoaded", function () {
  // Recuperar la lista de datos de productos del localStorage
  const productList = JSON.parse(localStorage.getItem("productoDataList"));
  const tableBody = document.querySelector("table tbody");

  if (productList) {
    const productListTabla = productList.filter(
      (producto) => producto.cantidad > 0
    );

    productListTabla.forEach(function (product) {
      const row = document.createElement("tr");
      row.innerHTML = `
            <td>${product.codigo}</td>
            <td>${product.descripcion}</td>
            <td>${product.cantidad}</td>
            <td>${product.precioBruto}</td>
            <td>${product.importe}</td>
          `;

      tableBody.appendChild(row);
    });
  } else {
    let filaVacio = `<tr><td colspan="5">NO HAY PRODUCTOS INGRESADOS</td></tr>`;
    tableBody.innerHTML = filaVacio;
  }

  ////////////////////////////////////////////////////////////////////
  ///////////// CALCULA SUBTOTAL Y TOTAL DE LO QUE TIENE LA TABLA ////
  ////////////////////////////////////////////////////////////////////

  const tipoImpuestoSelect = document.querySelector("#tipo_impuesto");

  // Función para actualizar los cálculos
  function updateCalculations() {
    const tipoImpuestoValue = tipoImpuestoSelect.value;

    if (productList && productList.length > 0) {
      const productListTabla = productList.filter(
        (producto) => producto.cantidad > 0
      );

      let subtotal = 0;

      productListTabla.forEach(function (product) {
        const precioBruto = parseFloat(product.precioBruto);
        const cantidad = parseInt(product.cantidad);
        const totalProducto = precioBruto * cantidad;

        subtotal += totalProducto;
      });

      // Calcula el impuesto (19%)
      let impuestos = 0;
      if (tipoImpuestoValue === "CON IMPUESTO") {
        impuestos = subtotal * 0.19;
        impuestos = Math.round(impuestos);
      }

      const total = subtotal + impuestos;

      // Actualiza los valores
      document.querySelector("[name='subtotal']").value = subtotal.toFixed(2);
      document.querySelector("[name='impuestos']").value = impuestos.toFixed(2);
      document.querySelector("[name='totalCompras']").value = total.toFixed(2);
    }
  }

  // Agregar un evento "change" al selector tipo_impuesto para actualizar los cálculos
  tipoImpuestoSelect.addEventListener("change", updateCalculations);

  // Llamar a la función inicialmente para calcular los valores con el valor inicial del selector
  updateCalculations();

  //////////////////////////////////////////////////////
  /// GUARDAR DATOS DEL FORMULARIO EN LOCALSTORAGE ////
  ////////////////////////////////////////////////////

  function saveToLocalStorage(fieldName) {
    const field = document.getElementById(fieldName);
    if (field) {
      let storedData = localStorage.getItem("storedData");
      if (!storedData) {
        storedData = {};
      } else {
        storedData = JSON.parse(storedData);
      }

      storedData[fieldName] = field.value;
      localStorage.setItem("storedData", JSON.stringify(storedData));
    }
  }

  // Función para cargar valores desde el arreglo en localStorage y establecerlos en los campos
  function loadFromLocalStorage(fieldName) {
    const field = document.getElementById(fieldName);
    if (field) {
      const storedData = JSON.parse(localStorage.getItem("storedData"));
      if (storedData && storedData[fieldName]) {
        field.value = storedData[fieldName];
      }
    }
  }

  // Agregar un evento "input" a cada campo de entrada para guardar los cambios en el arreglo en localStorage
  const inputFields = [
    "num_documento",
    "total",
    "fecha",
    "tipo_documento",
    "tipo_impuesto",
    "proveedor",
  ];

  inputFields.forEach(function (fieldName) {
    const field = document.getElementById(fieldName);
    if (field) {
      field.addEventListener("input", function () {
        saveToLocalStorage(fieldName);
      });
      // Cargar valores desde el arreglo en localStorage al cargar la página
      loadFromLocalStorage(fieldName);
    }
  });

  ///////////////////////////////////////
  //// GUARDAR DATOS DEL FORMULARIO  ///
  //////////////////////////////////////

  const mainButton = document.getElementById("btnSumit");

  mainButton.addEventListener("click", function (event) {
    const dataListProduc = localStorage.getItem("productoDataList");

    if (dataListProduc === null) {
      Swal.fire({
        title: "¿Estás seguro de cargar la compra?",
        text: "Su lista de productos esta vacia",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Enviar",
      }).then((result) => {
        if (result.isConfirmed) {
          document.getElementById("formDatosCompra").submit();
        }
      });
    } else {
      document.getElementById("formDatosCompra").submit();
    }
  });

  const limpiarButton = document.getElementById("btnLimpiar");

  limpiarButton.addEventListener("click", function () {
    localStorage.removeItem("productoDataList");
    localStorage.removeItem("storedData");

    location.reload();
  });
});

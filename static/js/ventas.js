document.addEventListener("DOMContentLoaded", function () {
  function actualizarTabla() {
    const productCarrito = JSON.parse(localStorage.getItem("carrito")) || [];
    const btnContainer = document.getElementById("containerBtnVentas");
    const tableBody = document.querySelector("#table-venta tbody");
    // Limpia la tabla
    tableBody.innerHTML = "";

    if (productCarrito.length !== 0 && productCarrito) {
      const productCarritoTabla = productCarrito.filter(
        (producto) => producto.cantidad > 0
      );
      // Obtener la referencia a la tabla donde se mostrarán los productos

      // Recorre los productos en el carrito y agrega filas actualizadas a la tabla
      productCarritoTabla.forEach((producto) => {
        let fila = document.createElement("tr");

        let codigo = document.createElement("td");
        codigo.textContent = producto.codigo;

        let nombreProducto = document.createElement("td");
        nombreProducto.textContent = producto.nombre;

        let cantidad = document.createElement("td");

        if (producto.medida === "UNIDAD") {
          cantidad.textContent = producto.cantidad;
        } else if (producto.medida === "KILO") {
          cantidad.textContent = `${producto.cantidad} gr`;
        }

        let precioUnitario = document.createElement("td");
        precioUnitario.textContent = producto.precio;

        let subtotal = document.createElement("td");

        let subtotalProducto = 0;

        if (producto.medida === "UNIDAD") {
          subtotalProducto = producto.cantidad * producto.precio;
        } else {
          // Calcular el subtotal para este producto en kilo o litro
          let cantidadEnKilos = producto.cantidad / 1000;

          let costoTotal = cantidadEnKilos * producto.precio;

          costoTotal = Math.round(costoTotal);

          subtotalProducto = costoTotal;
        }

        subtotal.textContent = subtotalProducto;

        let acciones = document.createElement("td");

        // Contenedor de botones
        let containerBtn = document.createElement("div");
        containerBtn.classList.add("d-flex", "gap-2");

        // Botón para eliminar producto
        let botonEliminar = document.createElement("button");
        botonEliminar.innerHTML = '<i class="bi bi-trash3"></i>';
        botonEliminar.classList.add("btn", "btn-outline-danger", "btn-sm");
        botonEliminar.addEventListener("click", () =>
          eliminarProductoVentas(producto.id)
        );

        if (producto.medida === "UNIDAD") {
          // Botón para aumentar cantidad
          let botonAumentar = document.createElement("button");
          botonAumentar.innerHTML = '<i class="bi bi-plus-circle"></i>';
          botonAumentar.classList.add("btn", "btn-outline-success", "btn-sm");
          botonAumentar.addEventListener("click", () =>
            aumentarCantidadVentas(producto.id)
          );

          // Botón para disminuir cantidad
          let botonDisminuir = document.createElement("button");
          botonDisminuir.innerHTML = '<i class="bi bi-dash-circle"></i>';
          botonDisminuir.classList.add("btn", "btn-outline-warning", "btn-sm");
          botonDisminuir.addEventListener("click", () =>
            disminuirCantidadVentas(producto.id)
          );

          containerBtn.appendChild(botonAumentar);
          containerBtn.appendChild(botonDisminuir);
        }

        containerBtn.appendChild(botonEliminar);

        acciones.appendChild(containerBtn);

        fila.classList.add("align-middle");
        fila.appendChild(codigo);
        fila.appendChild(nombreProducto);
        fila.appendChild(cantidad);
        fila.appendChild(precioUnitario);
        fila.appendChild(subtotal);
        fila.appendChild(acciones);

        tableBody.appendChild(fila);
      });

      if (btnContainer.classList.contains("none")) {
        btnContainer.classList.remove("none");
      }
    } else {
      btnContainer.classList.add("none");

      let filaVacio = `<tr><td colspan="6">NO HAY PRODUCTOS INGRESADOS</td></tr>`;

      tableBody.innerHTML = filaVacio;
    }
  }

  function eliminarProductoVentas(id) {
    eliminarDelCarrito(id);
    actualizarTabla();
    updateCalculoCarrito();
  }

  function aumentarCantidadVentas(id) {
    aumentarCantidad(id);
    actualizarTabla();
    updateCalculoCarrito();
  }

  function disminuirCantidadVentas(id) {
    disminuirCantidad(id);
    actualizarTabla();
    updateCalculoCarrito();
  }

  actualizarTabla();

  ////////////////////////////////////////////////////////////////////
  ///////////// CALCULA SUBTOTAL Y TOTAL DE LO QUE TIENE LA TABLA ////
  ////////////////////////////////////////////////////////////////////

  // Función para actualizar los cálculos
  function updateCalculoCarrito() {
    const productCarrito = JSON.parse(localStorage.getItem("carrito"));

    let total = 0;
    let totalImpuesto = 0;
    let subtotal = 0;
    let descuentoTotal = 0;

    if (productCarrito && productCarrito.length > 0) {
      const productCarritoTabla = productCarrito.filter(
        (producto) => producto.cantidad > 0
      );

      productCarritoTabla.forEach(function (product) {
        const precio = parseFloat(product.precio);
        const cantidad = parseInt(product.cantidad);
        const impuesto = product.impuesto;
        const medida = product.medida;
        const descuento = parseInt(product.descuento);

        // Total por producto
        let totalProducto = 0;
        if (medida === "UNIDAD") {
          totalProducto = precio * cantidad;
        } else {
          let cantidadEnKilos = cantidad / 1000;

          let costoTotal = cantidadEnKilos * precio;

          costoTotal = Math.round(costoTotal);

          totalProducto = costoTotal;
        }

        // Suma de los productos
        total += totalProducto;

        let montoDescuento = (descuento / 100) * totalProducto;

        descuentoTotal += Math.round(montoDescuento);

        if (impuesto === "IVA") {
          let IVA = 0.19;
          if (typeof IVAEMPRESA === "number" && IVAEMPRESA > 0) {
            //console.log(typeof IVAEMPRESA, IVAEMPRESA)
            IVA = IVAEMPRESA;
          }
          const totalImpuestoProducto = totalProducto * IVA;
          totalImpuesto += totalImpuestoProducto;
          totalImpuesto = Math.round(totalImpuesto);
        }
      });

      subtotal = total - totalImpuesto;
    }

    total = total - descuentoTotal;

    // Actualiza los valores

    document.querySelector("[name='subtotal']").value = subtotal.toFixed(2);
    document.querySelector("[name='impuestos']").value =
      totalImpuesto.toFixed(2);
    document.querySelector("[name='total']").value = total.toFixed(0);
    document.querySelector("[name='descuento']").value =
      descuentoTotal.toFixed(2);
  }

  updateCalculoCarrito();

  // LIMPIAR VENTA
  const btnBorrarVenta = document.getElementById("btnLimpiarVenta");

  btnBorrarVenta.addEventListener("click", function () {
    Swal.fire({
      titleText: `¿Estás seguro Borrar la Compra?`,
      icon: "question",
      showCancelButton: true,
      cancelButtonText: "No, Cancelar",
      confirmButtonText: "Si, Eliminar",
      confirmButtonColor: "#dc3545",
    }).then(function (result) {
      if (result.isConfirmed) {
        localStorage.removeItem("carrito");
        location.reload();
      }
    });
  });
});

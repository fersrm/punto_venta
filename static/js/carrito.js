// Función para agregar un producto al localStorage
function agregarAlCarrito(
  productoId,
  codigo,
  nombre,
  stock,
  precio,
  medida,
  impuesto,
  descuento = 0,
  cantidad = 1
) {
  // Comprobar si ya hay elementos en el carrito en el localStorage
  let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
  // Buscar el producto en el carrito por su ID
  let productoExistente = carrito.find((item) => item.id === productoId);

  // Reemplazar la coma por un punto y convertir a un número decimal
  stock = parseFloat(stock.replace(",", "."));

  // pasa Kilos a gramos
  if (medida === "KILO") {
    stock = stock * 1000;
    cantidad = parseInt(cantidad);
  }

  if (productoExistente) {
    if (productoExistente.medida === "KILO") {
      Swal.fire({
        text: "No puedes agregar más de este producto al carrito, borre el producto y vuelva a ingresarlo.",
        icon: "warning",
      });
      return;
    }

    // Si el producto ya está en el carrito, aumentar la cantidad
    if (productoExistente.cantidad < stock) {
      productoExistente.cantidad += 1;
    } else {
      Swal.fire({
        text: "No puedes agregar más de este producto al carrito, ha alcanzado el stock disponible.",
        icon: "warning",
      });
      return;
    }
  } else {
    if (1 <= stock) {
      carrito.push({
        id: productoId,
        codigo,
        nombre,
        stock,
        precio,
        medida,
        impuesto,
        cantidad,
        descuento,
      });
    } else {
      Swal.fire({
        text: "Stock insuficiente ya no queda en inventario.",
        icon: "warning",
        showConfirmButton: false,
        timer: 1500,
      });
      return;
    }
  }
  // Guardar el carrito actualizado en el localStorage
  localStorage.setItem("carrito", JSON.stringify(carrito));

  // Actualizar el contador del carrito
  actualizarCarrito();

  Swal.fire({
    text: "Producto agregado al carrito",
    icon: "success",
    showConfirmButton: false,
    timer: 1000,
    willClose: () => {
      const currentUrl = window.location.href;

      if (
        (currentUrl.includes("ventas") || currentUrl.includes("facturas")) &&
        medida !== "UNIDAD"
      ) {
        location.reload();
      }
    },
  });
}

function mostrarCarritoEnModal() {
  // Obtener el carrito del localStorage
  let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

  // Obtener el elemento modal-body donde se mostrará el contenido del carrito
  let carritoModalBody = document.getElementById("carrito-modal-body");
  let contenedorBtn = document.getElementById("carrito-btn");

  // Verificar si hay elementos en el carrito
  if (carrito.length === 0) {
    carritoModalBody.innerHTML = "<p>El carrito está vacío</p>";
    contenedorBtn.classList.add("none");
  } else {
    // Crear una tabla para mostrar los productos en el carrito
    let tablaCarrito = document.createElement("table");
    tablaCarrito.classList.add(
      "tableCarrito",
      "table",
      "table-striped",
      "table-hover"
    );

    // Crear encabezados de tabla, incluyendo el nuevo encabezado para Subtotal
    let encabezados =
      "<thead><tr><th>Nombre</th><th>Cantidad</th><th>Precio</th><th>Subtotal</th><th>Acciones</th></tr></thead>";
    tablaCarrito.innerHTML = encabezados;

    // Crear cuerpo de tabla
    let cuerpoTabla = document.createElement("tbody");

    // Inicializar el precio total del carrito
    let precioTotal = 0;

    // Recorrer los productos en el carrito y agregarlos a la tabla
    carrito.forEach((producto) => {
      let fila = document.createElement("tr");

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

      // Actualizar el precio total del carrito
      precioTotal += subtotalProducto;

      let acciones = document.createElement("td");

      //contenedor botones
      let containerBtn = document.createElement("div");
      containerBtn.classList.add("d-flex", "gap-2", "btn-carrito");

      // Botón para eliminar producto
      let botonEliminar = document.createElement("button");
      botonEliminar.innerHTML = '<i class="bi bi-trash3"></i>';
      botonEliminar.classList.add("btn", "btn-outline-danger", "btn-sm");
      botonEliminar.addEventListener("click", () =>
        eliminarDelCarrito(producto.id)
      );

      if (producto.medida === "UNIDAD") {
        // Botón para aumentar cantidad
        let botonAumentar = document.createElement("button");
        botonAumentar.innerHTML = '<i class="bi bi-plus-circle"></i>';
        botonAumentar.classList.add("btn", "btn-outline-success", "btn-sm");
        botonAumentar.addEventListener("click", () =>
          aumentarCantidad(producto.id)
        );

        // Botón para disminuir cantidad
        let botonDisminuir = document.createElement("button");
        botonDisminuir.innerHTML = '<i class="bi bi-dash-circle"></i>';
        botonDisminuir.classList.add("btn", "btn-outline-warning", "btn-sm");
        botonDisminuir.addEventListener("click", () =>
          disminuirCantidad(producto.id)
        );

        containerBtn.appendChild(botonAumentar);
        containerBtn.appendChild(botonDisminuir);
      }

      containerBtn.appendChild(botonEliminar);

      acciones.appendChild(containerBtn);

      fila.appendChild(nombreProducto);
      fila.appendChild(cantidad);
      fila.appendChild(precioUnitario);
      fila.appendChild(subtotal);
      fila.appendChild(acciones);

      cuerpoTabla.appendChild(fila);
    });

    tablaCarrito.appendChild(cuerpoTabla);

    // Crear fila para mostrar el precio total del carrito
    let filaTotal = document.createElement("tr");
    filaTotal.innerHTML = `<td colspan="3"><span style="font-weight: 700;">Total:</span></td><td><span style="font-weight: 700;">$${precioTotal}</span></td><td></td>`;
    cuerpoTabla.appendChild(filaTotal);

    // Limpiar el contenido previo y agregar la tabla al modal-body
    carritoModalBody.innerHTML = "";
    carritoModalBody.appendChild(tablaCarrito);

    // Verificar si el elemento tiene la clase "none"
    if (contenedorBtn.classList.contains("none")) {
      // Remover la clase "none" del elemento
      contenedorBtn.classList.remove("none");
    }
  }
}

function eliminarDelCarrito(idProducto) {
  let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
  carrito = carrito.filter((producto) => producto.id !== idProducto);
  localStorage.setItem("carrito", JSON.stringify(carrito));
  mostrarCarritoEnModal();
  // para el contador
  actualizarCarrito();
}

function aumentarCantidad(idProducto) {
  let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
  let producto = carrito.find((p) => p.id === idProducto);
  if (producto) {
    if (producto.cantidad < producto.stock) {
      producto.cantidad += 1;
      localStorage.setItem("carrito", JSON.stringify(carrito));
      mostrarCarritoEnModal();
    } else {
      Swal.fire({
        text: "No puedes agregar más de este producto al carrito, ha alcanzado el stock disponible.",
        icon: "warning",
      });
    }
  }
}

function disminuirCantidad(idProducto) {
  let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
  let producto = carrito.find((p) => p.id === idProducto);
  if (producto && producto.cantidad > 1) {
    producto.cantidad -= 1;
    localStorage.setItem("carrito", JSON.stringify(carrito));
    mostrarCarritoEnModal();
  }
}

mostrarCarritoEnModal();

function vaciarCarrito() {
  localStorage.removeItem("carrito");

  mostrarCarritoEnModal();

  // para el contador
  actualizarCarrito();

  Swal.fire({
    text: "El carrito ha sido vaciado",
    icon: "success",
    showConfirmButton: false,
    timer: 1500,
  });
}

$("#carritoModal").on("show.bs.modal", function (e) {
  mostrarCarritoEnModal();
});

function tipoMedida(medida) {
  const medidaSelect = document.getElementById("mediaSelect");
  let tipoMedida = medida;

  if (tipoMedida === "KILO") {
    medidaSelect.options.length = 0;

    let optionGr = document.createElement("option");
    optionGr.value = "1";
    optionGr.text = "Gr";
    medidaSelect.add(optionGr);

    let optionKg = document.createElement("option");
    optionKg.value = "2";
    optionKg.text = "Kg";
    medidaSelect.add(optionKg);
  }
}

// datos Producto variable Global
var productoSeleccionado = null;

// Función para almacenar datos del producto
function datosProducto(
  id,
  codigo,
  descripcion,
  stock,
  precio,
  medida,
  impuesto,
  descuento
) {
  productoSeleccionado = {
    id,
    codigo,
    descripcion,
    stock,
    precio,
    medida,
    impuesto,
    descuento,
  };

  tipoMedida(medida);
}

function closeCantidadModal() {
  let cantidad = document.getElementById("IntCantidad").value;
  let selectCantidad = document.getElementById("mediaSelect").value;

  selectCantidad = parseInt(selectCantidad);

  if (selectCantidad === 2) {
    cantidad = cantidad * 1000;
  }

  agregarAlCarrito(
    productoSeleccionado.id,
    productoSeleccionado.codigo,
    productoSeleccionado.descripcion,
    productoSeleccionado.stock,
    productoSeleccionado.precio,
    productoSeleccionado.medida,
    productoSeleccionado.impuesto,
    productoSeleccionado.descuento,
    cantidad
  );
  // Restablecer la variable global después de usarla
  productoSeleccionado = null;

  const closeModal = document.getElementById("closeModalCantidad");
  const cantidadIpunt = document.getElementById("IntCantidad");
  cantidadIpunt.value = "";
  closeModal.click();
}

// contador carrito
function actualizarCarrito() {
  let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
  let totalProductos = carrito.length;
  let cartCount = document.getElementById("cart-count");

  cartCount.textContent = totalProductos;

  if (totalProductos > 0) {
    cartCount.style.display = "inline-block";
  } else {
    cartCount.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", actualizarCarrito);

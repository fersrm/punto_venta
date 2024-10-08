document.addEventListener("DOMContentLoaded", function () {
  function crearTablaBoleta() {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

    if (carrito.length !== 0) {
      let tablaCarrito = document.createElement("table");

      let encabezados =
        "<thead><tr><th>Codigo</th><th>Nombre</th><th>Cantidad</th><th>Precio</th><th>Subtotal</th></tr></thead>";
      tablaCarrito.innerHTML = encabezados;

      // Crear cuerpo de tabla
      let cuerpoTabla = document.createElement("tbody");

      // Recorrer los productos en el carrito y agregarlos a la tabla
      carrito.forEach((producto) => {
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
        // Calcular el subtotal para este producto

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

        fila.appendChild(codigo);
        fila.appendChild(nombreProducto);
        fila.appendChild(cantidad);
        fila.appendChild(precioUnitario);
        fila.appendChild(subtotal);

        cuerpoTabla.appendChild(fila);
      });

      tablaCarrito.appendChild(cuerpoTabla);

      // Crear fila para mostrar el precio total del carrito
      let filaSubtotal = document.createElement("tr");
      let filaIVA = document.createElement("tr");
      let filaTotal = document.createElement("tr");
      let filaDescuentoTotal = document.createElement("tr");

      let total = document.querySelector("[name='total']").value;
      let subtotal = document.querySelector("[name='subtotal']").value;
      let iva = document.querySelector("[name='impuestos']").value;
      let descuento = document.querySelector("[name='descuento']").value;

      filaSubtotal.innerHTML = `<td colspan="3">&nbsp;</td><td><strong>Sub Total:</strong></td><td>${subtotal}</td>`;
      filaIVA.innerHTML = `<td colspan="3">&nbsp;</td><td><strong>IVA:</strong></td><td>${iva}</td>`;
      filaDescuentoTotal.innerHTML = `<td colspan="3">&nbsp;</td><td><strong>Descuento:</strong></td><td>- ${descuento}</td>`;
      filaTotal.innerHTML = `<td colspan="3">&nbsp;</td><td><strong>Total:</strong></td><td>${total}</td>`;

      cuerpoTabla.appendChild(filaSubtotal);
      cuerpoTabla.appendChild(filaIVA);
      cuerpoTabla.appendChild(filaDescuentoTotal);
      cuerpoTabla.appendChild(filaTotal);

      return tablaCarrito;
    }
  }

  function crearTablaDatosCliente() {
    let clienteDatos = JSON.parse(localStorage.getItem("cliente")) || [];

    if (clienteDatos.length !== 0) {
      let tablaCliente = document.createElement("table");

      let encabezados =
        "<thead><tr><th>RUN</th><th>Nombre</th><th>Correo</th><th>Telefono</th></tr></thead>";
      tablaCliente.innerHTML = encabezados;

      // Crear cuerpo de tabla
      let tableBodyCliente = document.createElement("tbody");

      let filaCLiente = document.createElement("tr");

      let run = document.createElement("td");
      run.textContent = clienteDatos.run;

      let nombreCliente = document.createElement("td");
      nombreCliente.textContent = clienteDatos.nombreCompleto;

      let correoCliente = document.createElement("td");
      correoCliente.textContent = clienteDatos.correo;

      let telefonoCliente = document.createElement("td");
      telefonoCliente.textContent = clienteDatos.telefono;

      filaCLiente.appendChild(run);
      filaCLiente.appendChild(nombreCliente);
      filaCLiente.appendChild(correoCliente);
      filaCLiente.appendChild(telefonoCliente);

      tableBodyCliente.appendChild(filaCLiente);

      tablaCliente.appendChild(tableBodyCliente);

      return tablaCliente;
    }
  }

  const tabla1 = crearTablaBoleta();
  const tabla2 = crearTablaDatosCliente();

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  const tableTitle = "Factura";

  doc.text(tableTitle, 95, 20);

  let startY1 = 30;
  doc.autoTable({ html: tabla2, startY: startY1 });

  let startY2 = doc.autoTable.previous.finalY + 10;
  doc.autoTable({ html: tabla1, startY: startY2 + 10 });

  doc.output("dataurlnewwindow");

  // Elimina el carrito de  local Storage
  localStorage.removeItem("carrito");
  location.reload();
});

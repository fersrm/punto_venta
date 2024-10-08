document.addEventListener("DOMContentLoaded", function () {
  const btnPdfVenta = document.getElementById("btnSumitVenta");

  btnPdfVenta.addEventListener("click", (e) => {
    const carrito = obtenerCarritoDesdeLocalStorage();

    document.getElementById("carrito-input").value = JSON.stringify(carrito);

    document.getElementById("formDatosVenta").submit();
  });

  function obtenerCarritoDesdeLocalStorage() {
    const carritoString = localStorage.getItem("carrito");
    const carrito = JSON.parse(carritoString) || [];
    return carrito;
  }
});

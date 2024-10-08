(() => {
  "use strict";

  // Obtén el elemento canvas del gráfico
  const ctx = document.getElementById("myChart");

  // Obtiene las fechas y los valores de ventas del diccionario ventas_diarias
  const fechas = Object.keys(ventas_diarias);
  const valoresVentas = Object.values(ventas_diarias);

  //////////////////////////////////////////
  const valoresGastos = gastos_totales;

  // Configura el gráfico
  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: fechas, // Usa las fechas como etiquetas en el eje x
      datasets: [
        {
          label: "Ventas",
          data: valoresVentas, // Usa los valores de ventas en eje y
          lineTension: 0,
          backgroundColor: "rgba(0, 123, 255, 0.5)",
          borderColor: "#007bff",
          borderWidth: 4,
          pointBackgroundColor: "#007bff",
        },
        {
          label: "Gastos",
          data: valoresGastos,
          backgroundColor: "rgba(255, 99, 132, 0.5)",
          borderColor: "#ff6384",
          borderWidth: 4,
          pointBackgroundColor: "#ff6384",
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
      plugins: {
        legend: {
          display: "top",
        },
        tooltip: {
          boxPadding: 3,
        },
      },
    },
  });
})();

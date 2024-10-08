//-----------------Auto Focus ------------------

function auto_focus() {
  const buscar = document.getElementById("buscar");
  buscar.value = "";
  buscar.focus();
}

history.replaceState({}, document.title, window.location.pathname);
auto_focus();

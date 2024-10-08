function confirmAndDeleteEntity(entityType, id, nombre) {
  const entity = {
    tienda: "Producto",
    usuarios: "Usuario",
    clientes: "Cliente",
    proveedores: "Proveedor",
  };

  Swal.fire({
    titleText: `¿Estás seguro de eliminar al ${entity[entityType]}?`,
    text: nombre,
    icon: "question",
    showCancelButton: true,
    cancelButtonText: "No, Cancelar",
    confirmButtonText: "Sí, Eliminar",
    confirmButtonColor: "#dc3545",
  }).then(function (result) {
    if (result.isConfirmed) {
      window.location.href = `/${entityType}/borrar/${id}/`;
    }
  });
}

// Usage examples
function eliminar_producto(id, nombre) {
  confirmAndDeleteEntity("tienda", id, nombre);
}

function eliminar_usuario(id, nombre) {
  confirmAndDeleteEntity("usuarios", id, nombre);
}

function eliminar_cliente(id, nombre) {
  confirmAndDeleteEntity("clientes", id, nombre);
}

function eliminar_proveedor(id, nombre) {
  confirmAndDeleteEntity("proveedores", id, nombre);
}

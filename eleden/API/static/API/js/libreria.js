// function confirmar_eliminar(ruta){
//     if(confirm("Está seguro?")){
//         location.href = ruta;
//     }
//     else{on
//         alert("Fiuu, te salvaste...")
//     }
// }

var proveedores = {{ proveedores | safe }}; 

document.getElementById('formMateriaPrima').addEventListener('submit', function(event) {
    var nombre_proveedor = document.getElementById('nombre').value;
    
    if (!proveedores.includes(nombre_proveedor)) {
        event.preventDefault();
        
        Swal.fire({
            title: "</strong>Proveedor no encontrado</strong>",
            icon: "info",
            html: `
              <b>¿Desea agregar este proveedor?</b>,
              
            `,
            showCloseButton: true,
            showCancelButton: true,
            focusConfirm: false,
            confirmButtonText: `
              Agregar
            `,
            confirmButtonAriaLabel: "Thumbs up, great!",
            cancelButtonText: `
              Cancelar
            `,
            cancelButtonAriaLabel: "Thumbs down"
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = "/ruta/a/formulario/de/proveedores";
            }
        });
    }
});

function verProducto(ruta) {
    var contenedor = $("#offcanvasRight");

    $.ajax({
        method: "GET",
        url: ruta
    })
    .done(function(respuesta) {
        contenedor.html(respuesta);
        quitarAlertas(); // Supongo que esta función quita las alertas después de cargar el contenido
    })
    .fail(function() {
        alert("Error al cargar los datos del producto");
    });
}


function ver_carrito(ruta){
    // data: { name: "John", location: "Boston" }
    r = $("#offcanvasRight")

    $.ajax({
        method: "GET",
        url: ruta
    })
    .done(function( respuesta ) {
        r.html(respuesta)
        quitar_alertas();
    })
    .fail(function() {
        alert( "error" );
    });
}

function add_carrito(ruta, id){
    r = $("#offcanvasRight")

    id_producto = $("#id_producto_"+id).val()
    cantidad = $("#cantidad_"+id).val()

    //dataType: 'json'
    $.ajax({
        method: "GET",
        url: ruta,
        data: { "id_producto": id_producto, "cantidad": cantidad }
    })
    .done(function( respuesta ) {
        r.html(respuesta);
        // abrir offcanvas
        offcanvas = $("#offcanvasRight").offcanvas('toggle');
        quitar_alertas();
    })
    .fail(function() {
        alert( "error" );
    });
}

function del_item_carrito(ruta){
    r = $("#offcanvasRight")

    $.ajax({
        method: "GET",
        url: ruta
    })
    .done(function( respuesta ) {
        r.html(respuesta);
        quitar_alertas();
        // abrir offcanvas
        // offcanvas = $("#offcanvasRight").offcanvas('toggle');
    })
    .fail(function() {
        alert( "error" );
    });
}

function quitar_alertas(){
    console.log( "Quitando alerta..." );
    window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
            $(this).remove();
        });
    }, 1000);
}

const button = document.querySelector('.button')
const nav = document.querySelector('.nav')
const btn_header = document.querySelector('.btn-header')

button.addEventListener('click',()=>{
    nav.classList.toggle('activo')
    btn_header.classList.toggle('activo')
})

function confirmar_eliminar(ruta) {
    Swal.fire({
        title: '¿Está seguro?',
        text: "¡No podrás revertir esto!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminarlo',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            location.href = ruta;
        } else {
            Swal.fire(
                'Cancelado',
                'Tu archivo está seguro :)',
                'info'
            );
        }
    });
}

function confirmar_guardar(event) {
    event.preventDefault(); // Evitar el envío del formulario por defecto

    Swal.fire({
        title: '¿Está seguro?',
        text: "Una vez guardado, no podrás modificar este pedido.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, guardar pedido',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            // Enviar el formulario manualmente si se confirma
            document.getElementById("pedidoForm").submit();
        } else {
            Swal.fire(
                'Cancelado',
                'El pedido no ha sido guardado.',
                'info'
            );
        }
    });
}


$(document).ready(function() {
    var footer = $(".pie-pagina");
    var windowHeight = $(window).height();
    var footerHeight = footer.outerHeight();

    $(window).scroll(function() {
        var scrollTop = $(this).scrollTop();
        var contentHeight = $(".content").outerHeight();
        var footerPosition = contentHeight - scrollTop + windowHeight - footerHeight;

        if (footerPosition < windowHeight) {
            footer.css({
                "position": "fixed",
                "bottom": "0",
                "left": "0"
            });
        } else {
            footer.css({
                "position": "relative"
            });
        }
    });
});

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



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
        quitarAlertas();
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



function add_carrito(url, id_producto) {
    console.log(url)
    console.log(id_producto)
    const csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    const id = document.getElementById(`id_producto`).value;
    const cantidad = document.getElementById(`cantidad_${id_producto}`).value;
    const items_carrito = document.getElementById("items_carrito");
    console.log(id)
    // Mostrar loader
    const loader = document.getElementById("loader");
    loader.classList.remove("d-none");
    loader.classList.add("d-block");

    // Mostrar carrito offCanvas
    const offCanvas_carrito = new bootstrap.Offcanvas(document.getElementById("offcanvasRight"));
    offCanvas_carrito.show();

    // Realizar la solicitud AJAX con el método POST
    $.ajax({
        url: url,
        type: "POST",  // Método POST
        data: {
            "csrfmiddlewaretoken": csrf_token,
            "id": id,
            "cantidad": cantidad
        },
    })
    .done(function(respuesta) {
        if (respuesta != "Error") {
            loader.classList.remove("d-block");
            loader.classList.add("d-none");

            // Actualizar el contenido del carrito
            const contenido = document.getElementById("respuesta_carrito");
            contenido.innerHTML = respuesta;

            // Actualizar los ítems del carrito
            const position_ini = respuesta.search(" ");
            const position_final = respuesta.search("</h1>");
            const result = respuesta.substring(position_ini + 2, position_final - 1);
            items_carrito.innerHTML = result;
        } else {
            location.href = "API/carrito/tienda/";
        }
    })
    .fail(function(respuesta) {
        location.href = "API/carrito/tienda/";
    });
}



function ver_carrito(url){
    // Capturo referencia a dom de carrito del offCanvas
    contenido = $("#respuesta_carrito")
    loader = $("#loader")

    loader.removeClass("d-none");
    loader.addClass("d-block");

    offCanvas_carrito = $("#offcanvasRight");
    offCanvas_carrito.offcanvas('toggle');

    $.ajax({
        url: url
    })
    .done(function(respuesta){

        if (respuesta != "Error"){
            /*setTimeout(()=>{
                loader.removeClass("d-block");
                loader.addClass("d-none");
                // Pintar respuesta en offCanvas
                contenido.html(respuesta);
            }, 3000);*/

            loader.removeClass("d-block");
            loader.addClass("d-none");
            // Pintar respuesta en offCanvas
            contenido.html(respuesta);

        }
        else{
            location.href="API/carrito/tienda/";
        }
    })
    .fail(function(respuesta){
        location.href="API/carrito/tienda/";
    });
}

function eliminar_item_carrito(url) {
    console.log("URL a la que se envía la petición:", url); // Depurar URL
    contenido = $("#respuesta_carrito");
    items_carrito = $("#items_carrito");
    loader = $("#loader");

    loader.removeClass("d-none");
    loader.addClass("d-block");

    $.ajax({
        url: url
    })
    .done(function(respuesta){
        if (respuesta != "Error") {
            loader.removeClass("d-block");
            loader.addClass("d-none");
            contenido.html(respuesta);

            // Buscar items en html resultante
            let position_ini = respuesta.search(" ");
            let position_final = respuesta.search("</h1>");
            let result = respuesta.substring(position_ini + 2, position_final - 1);
            items_carrito.html(result);
        } else {
            location.href = "API/carrito/tienda/";
        }
    })
    .fail(function(respuesta) {
        location.href = "API/carrito/tienda/";
    });
}

function actualizar_totales_carrito(url, id){
    contenido = $("#respuesta_carrito")
    loader = $("#loader")
    cantidad = $("#cantidad_carrito_"+id)

    loader.removeClass("d-none");
    loader.addClass("d-block");

    $.ajax({
        url: url,
        type: "GET",
        data: {"cantidad": cantidad.val()}
    })
    .done(function(respuesta){

        if (respuesta != "Error"){

            loader.removeClass("d-block");
            loader.addClass("d-none");
            // Pintar respuesta en offCanvas
            contenido.html(respuesta);
        }
        else{
            location.href="API/carrito/tienda/";
        }
    })
    .fail(function(respuesta){
        location.href="API/carrito/tienda/";
    });
}

function add_carrito1(url, producto_id) {
    console.log('Agregando al carrito:', producto_id);  // Verificación
    const cantidad = document.getElementById(`cantidad_${producto_id}`).value; 

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ id_producto: producto_id, cantidad: cantidad })
    }).then(response => {
        if (response.ok) {
            alert('Producto agregado al carrito');
        } else {
            alert('Hubo un error al agregar el producto al carrito.');
        }
    }).catch(error => {
        console.error('Error:', error);
    });
}



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
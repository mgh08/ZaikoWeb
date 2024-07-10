
document.addEventListener("DOMContentLoaded", function() {
    const btnRegresar = document.querySelector('.btn-regresar');
    
    if (btnRegresar) {
        btnRegresar.addEventListener('click', function(event) {
            event.preventDefault();
            document.body.classList.add('fade-out');

            // Esperar a que la transición termine antes de navegar
            setTimeout(function() {
                window.location.href = btnRegresar.href;
            }, 500); // Tiempo en milisegundos (debe coincidir con la duración de la transición en CSS)
        });
    }
});


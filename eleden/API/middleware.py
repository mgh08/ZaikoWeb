from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rutas_protegidas = [
            reverse('panelDeGestion'),
            reverse('graficos'),
            reverse('auditoria'),
            reverse('enviarCorreo'),
            reverse('clientes'),
            reverse('buscar'),
            reverse('clientes_formulario'),
            reverse('clientes_guardar'),
            reverse('clientes_actualizar'),
            reverse('pruebaDemo'),
            reverse('invBasico'),
            reverse('invAvanzado'),
            reverse('invPremium'),
            reverse('pruebaGratis'),
            reverse('registrarProveedores'),
            reverse('proveedores'),
            reverse('registrar_devoluciones'),
            reverse('listarDevoluciones'),
            reverse('devoluciones_guardar'),
            reverse('devoluciones_actualizar'),
            reverse('registrarProveedores'),
            reverse('listarProveedores'),
            reverse('proveedores_guardar'),
            reverse('proveedores_actualizar'),
            reverse('registrar_producto'),
            reverse('productoTerminado'),
            reverse('buscar_productos'),
            reverse('productos_guardar'),
            reverse('categorias'),
            reverse('categorias_formulario'),
            reverse('categorias_guardar'),
            reverse('categorias_actualizar'),
            reverse('buscar_categorias'),
            reverse('pedidos'),
            reverse('pedidos_formulario'),
            reverse('pedidos_guardar'),
            reverse('pedidos_listar'),
            reverse('carrito_ver'),
            reverse('carrito_add'),
            reverse('guardar_compra'),
            reverse('vaciar_carrito'),
            reverse('tienda'),
            reverse('productos_listar_software'),
            reverse('productos_actualizar_software'),
            reverse('productos_guardar_software'),
            reverse('productos_formulario_software')

        ]
        if request.path in rutas_protegidas and not request.session.get('logueo'):
            # Redirigir al usuario con un mensaje personalizado
            return render(request, 'API/index/login.html', {"mensaje": "Acceso denegado. Debes iniciar sesión para acceder a esta página."})

        response = self.get_response(request)
        return response

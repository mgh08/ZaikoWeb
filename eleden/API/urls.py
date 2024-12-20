from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework.authtoken.views import obtain_auth_token
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from . import views

router = DefaultRouter()
# router.register(r'AlertaStock', views.AlertaStockViewSet),
router.register(r'Almacen', views.AlmacenViewSet),
router.register(r'CategoriaProducto', views.CategoriaProductoViewSet),
router.register(r'Cliente', views.ClienteViewSet),
router.register(r'Devolucion', views.DevolucionViewSet),
# router.register(r'MateriaPrima', views.MateriaPrimaViewSet),
# router.register(r'MovimientoStock', views.MovimientoStockViewSet),
router.register(r'ProductoTerminado', views.ProductoTerminadoViewSet),
router.register(r'Proveedor', views.ProveedorViewSet),
# router.register(r'Receta', views.RecetaViewSet),
#router.register(r'DetallePedido', views.DetallePedidoViewSet),
router.register(r'Pedido', views.PedidoViewSet),
router.register(r'Usuario', views.UsuarioViewSet),
router.register(r'ventaSoftware', views.VentaSoftwareViewSet),

from django.conf.urls import handler404
from . import views

handler404 = 'API.views.custom_404'

# Tus otras rutas


urlpatterns = [
    path('', views.index, name='index'),
    #path("baseAdmin/", views.baseAdmin, name="baseAdmin"),

    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("registrarse/", views.registrarse, name="registrarse"),
    path("formulario_cambiar_clave/", views.formulario_cambiar_clave, name="formulario_cambiar_clave"),
    path("olvide_mi_clave/<str:correo>/", views.olvide_mi_clave, name="olvide_mi_clave"),
    path("recuperar_clave_form/", views.recuperar_clave_form, name="recuperar_clave_form"),
    path("verificar_token_form/<str:correo>/", views.verificar_token_form, name="verificar_token_form"),


    

    path("panelDeGestion/", views.panelDeGestion, name="panelDeGestion"),
    path("graficos/", views.graficos, name="graficos"),
    path("auditoria/", views.auditoria, name="auditoria"),

    #Enviar correo
    path("enviarCorreo/", views.enviarCorreo, name="enviarCorreo"),

    #clientes
    path("clientes/", views.clientes, name="clientes"),
    path("buscar/", views.buscar, name="buscar"),
    path("clientes_formulario/", views.clientes_formulario, name="clientes_formulario"),
    path("clientes_guardar/", views.clientes_guardar, name="clientes_guardar"),
    path("clientes_formulario_editar/<int:id_cliente>/", views.clientes_formulario_editar, name="clientes_formulario_editar"),
    path("clientes_actualizar/", views.clientes_actualizar, name="clientes_actualizar"),
    path("clientes_eliminar/<int:id>/", views.clientes_eliminar, name="clientes_eliminar"),

    #paquetes
    path('pruebaDemo/', views.pruebaDemo, name='pruebaDemo'),
    path('invBasico/', views.invBasico, name='invBasico'),
    path('invAvanzado/', views.invAvanzado, name='invAvanzado'),
    path('invPremium/', views.invPremium, name='invPremium'),
    path('pruebaGratis/', views.pruebaGratis, name='pruebaGratis'),

    #API
    path("api/1.0/", include(router.urls)),
    path('api/1.0/token-auth/', views.CustomAuthToken.as_view(), name='token-auth'),
    # Ruta para login en API web
    path('api/1.0/auth/', include("rest_framework.urls")),

    path("registrarProveedores/", views.registrarProveedores, name="registrarProveedores"),
    path("proveedores/", views.proveedores, name="proveedores"),

    #devoluciones
    path("registrar_devoluciones/", views.registrar_devoluciones, name="registrar_devoluciones"),
    path("listarDevoluciones/", views.listarDevoluciones,name="listarDevoluciones"),
    #path("devoluciones_formulario/", views.devoluciones_formulario,name="devoluciones_formulario"),
    path("devoluciones_guardar/",views.devoluciones_guardar, name="devoluciones_guardar"),
    path("devoluciones_editar/<int:id>/",views.devoluciones_editar,name="devoluciones_editar"),
    path("devoluciones_actualizar/",views.devoluciones_actualizar,name="devoluciones_actualizar"),
    path("devoluciones_eliminar/<int:id>/", views.devoluciones_eliminar, name="devoluciones_eliminar"),
    

    #proveedores
    path("registrarProveedores/", views.registrarProveedores,name="registrarProveedores"),
    path("listarProveedores/", views.listarProveedores,name="listarProveedores"),
    path("proveedores_guardar/",views.proveedores_guardar, name="proveedores_guardar"),
    path("proveedores_editar/<int:id>/", views.proveedores_editar, name="proveedores_editar"),
    path("proveedores_actualizar/", views.proveedores_actualizar,name="proveedores_actualizar"),
    path("proveedores_eliminar/<int:id>/", views.proveedores_eliminar, name="proveedores_eliminar"),


    #productos
    path("registrar_producto/", views.registrar_producto, name="registrar_producto"), #posible eliminacion
    path("productoTerminado/", views.productoTerminado, name="productoTerminado"),
    path("buscar_productos/", views.buscar_productos, name="buscar_productos"),
    path("productos_actualizar/<int:id>/", views.productos_actualizar, name="productos_actualizar"),
    path("productos_eliminar/<int:id>/", views.productos_eliminar, name="productos_eliminar"),
    path("productos_guardar/", views.productos_guardar, name="productos_guardar"),
    path("productos_formulario_editar/<int:id>/", views.productos_formulario_editar, name="productos_formulario_editar"),
    path("ver_productos/<int:id>/", views.ver_productos, name="ver_productos"),

    
    #categorias
    path("categorias/", views.categorias, name="categorias"),
	path("categorias_formulario/", views.categorias_formulario, name="categorias_formulario"),
	path("categorias_guardar/", views.categorias_guardar, name="categorias_guardar"),
	path("categorias_eliminar/<int:id>/", views.categorias_eliminar, name="categorias_eliminar"),
	path("categorias_formulario_editar/<int:id>/", views.categorias_formulario_editar, name="categorias_formulario_editar"),
	path("categorias_actualizar/", views.categorias_actualizar, name="categorias_actualizar"),
    path("buscar_categorias/", views.buscar_categorias, name="buscar_categorias"),

    #Pedidos
    path("pedidos/", views.pedidos, name="pedidos"),
    path("pedidos_formulario/", views.pedidos_formulario, name="pedidos_formulario"),
    path("pedidos_guardar/", views.pedidos_guardar, name="pedidos_guardar"),
    path("pedidos_listar/", views.pedidos_listar, name="pedidos_listar"),
    path("pedidos_eliminar/<int:id>/",views.pedidos_eliminar,name="pedidos_eliminar"),

    #carrito
    path("carrito_ver/", views.carrito_ver, name="carrito_ver"),
    path("carrito_add/", views.carrito_add, name='carrito_add'),
    path('eliminar_item/<int:id_producto>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path("guardar_compra/", views.guardar_compra, name='guardar_compra'),
    path("vaciar_carrito/", views.vaciar_carrito, name='vaciar_carrito'),
    path("tienda/", views.tienda, name='tienda'),

    # Producto Software
    path("productos_listar_software/", views.productos_listar_software, name='productos_listar_software'),
    path("productos_actualizar_software/", views.productos_actualizar_software, name='productos_actualizar_software'),
    path("productos_eliminar_software/<int:id_producto>/", views.productos_eliminar_software, name='productos_eliminar_software'),
    path("productos_editar_software/<int:id_producto>/", views.productos_editar_software, name='productos_editar_software'),
    path("productos_guardar_software", views.productos_guardar_software, name='productos_guardar_software'),
    path("productos_formulario_software", views.productos_formulario_software, name='productos_formulario_software'),

        
    





]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

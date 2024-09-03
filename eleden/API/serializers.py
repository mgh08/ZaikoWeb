from .models import *
from rest_framework import serializers


#class PeliculaSerializer(serializers.ModelSerializer):
	#class Meta:
		#model = Pelicula
		# fields = ['id', 'titulo', 'imagen', 'estreno', 'resumen']
# 		#fields = '__all__'

# class AlertaStockSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = AlertaStock
# 		fields = '__all__'

class AlmacenSerializer(serializers.ModelSerializer):
	class Meta:
		model = Almacen
		fields = '__all__'

class CategoriaProductoSerializer(serializers.ModelSerializer):
	class Meta:
		model = CategoriaProducto
		fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Cliente
		fields = '__all__'

class DevolucionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Devolucion
		fields = '__all__'


# class MateriaPrimaSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = MateriaPrima
# 		fields = '__all__'

# class MovimientoStockSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = MovimientoStock
# 		fields = '__all__'

class ProductoTerminadoSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductoTerminado
		fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
	class Meta:
		model = Proveedor
		fields = '__all__'		


# class RecetaSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = Receta
# 		fields = '__all__'

# class DetallePedidoSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = DetallePedido
# 		fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Pedido
		fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
	class Meta:
		model = Usuario
		fields = '__all__'

class ventaSoftwareSerializer(serializers.ModelSerializer):
	class Meta:
		model = ventaSoftware
		fields = '__all__'



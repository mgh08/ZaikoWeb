from django.db import models

from .authentication import CustomUserManager

from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MinLengthValidator

from django.conf import settings  # Importa la configuración de Django
# from django.contrib.auth.models import User  # Esto ya no es necesario

class VentaSoftware(models.Model):
    nombre = models.CharField(max_length=200)
    stock = models.IntegerField()
    precio = models.IntegerField()
    descripcion = models.TextField(help_text="Descripción del producto")
    foto = models.ImageField(upload_to="fotos_paquetes/", default="fotos_paquetes/default.png")

    def subtotal(self, cantidad):
        return self.precio * cantidad

    def __str__(self):
        return f"{self.nombre}"


class Usuario(AbstractUser):
    username = None
    nombreCompleto = models.CharField(max_length=254)
    usuario = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=254, validators=[MinLengthValidator(8)])  # Mínimo 8 caracteres
    ROLES = (
        ("ADMIN", "Administrador"),
        ("GEREN", "Gerente"),
        ("USUAR", "Usuario"),
    )
    rol = models.CharField(max_length=5, choices=ROLES, default="USUAR", null=True, blank=True)
    foto = models.ImageField(upload_to="fotos/", default="fotos/default.png")
    token = models.CharField(max_length=10, null=True, blank=True)

    USERNAME_FIELD = "usuario"
    REQUIRED_FIELDS = ["nombreCompleto"]

    def __str__(self):
        return f"{self.nombreCompleto} - {self.rol}"

class Venta(models.Model):
	fecha_venta = models.DateTimeField(auto_now=True)
	usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
	ESTADOS = (
		(1, 'Pendiente'),
		(2, 'Enviado'),
		(3, 'Rechazada'),
	)
	estado = models.IntegerField(choices=ESTADOS, default=1)

	def __str__(self):
		return f"{self.id} - {self.usuario}"


class DetalleVenta(models.Model):
	venta = models.ForeignKey(Venta, on_delete=models.DO_NOTHING)
	producto = models.ForeignKey(VentaSoftware, on_delete=models.DO_NOTHING)
	cantidad = models.IntegerField()
	precio_historico = models.IntegerField()

	def __str__(self):
		return f"{self.id} - {self.venta}"
   




class Almacen(models.Model):
    nombre = models.CharField(max_length=255)
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)


# class CategoriaProducto(models.Model):
#     nombre = models.CharField(max_length=255) 
#     ubicacion = models.CharField(max_length=255)


class CategoriaProducto(models.Model):
    nombre_categoria = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre_categoria}"


class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    nit = models.CharField(max_length=255, unique=True)  # El NIT debe ser único
    contacto = models.CharField(max_length=255)
    correo_electronico = models.EmailField(null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre}"

from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone

class ProductoTerminado(models.Model):
    nombre = models.CharField(max_length=255, validators=[
        RegexValidator(regex='^[A-Za-z\s]+$', message='El nombre debe contener solo letras y espacios.')
    ])
    categorias = models.ForeignKey(CategoriaProducto, on_delete=models.DO_NOTHING)
    unidad_medida = models.CharField(max_length=50)
    lote = models.CharField(max_length=50, validators=[
        RegexValidator(regex='^[A-Za-z0-9\-]+$', message='El lote debe contener solo letras, números y guiones.')
    ])
    fecha_vencimiento = models.DateField(null=True, blank=True)

    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(0)], null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True)

    foto = models.ImageField(default='fotos/default.png', upload_to='fotos_productos/')

    def clean(self):
        # Validar que la fecha de vencimiento no sea anterior a la fecha actual
        if self.fecha_vencimiento and self.fecha_vencimiento < timezone.now().date():
            raise ValidationError("La fecha de vencimiento no puede ser anterior a la fecha actual.")

    def __str__(self):
        return self.nombre

    
class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_pedido = models.DateField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)


class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, related_name="productos", on_delete=models.CASCADE)
    producto = models.ForeignKey(ProductoTerminado, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)

    

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class Devolucion(models.Model): 
    fecha_devolucion = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        validators=[
            RegexValidator(regex='^[A-Za-z\s]+$', message='El motivo debe contener solo letras y espacios')
        ]
    )
    foto = models.ImageField(default='fotos/default.png', upload_to='fotos/fotos_productos/')
    productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)

    def clean(self):
        # Validar que el archivo sea una imagen válida
        if self.foto:
            if not self.foto.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise ValidationError("Solo se permiten imágenes en formato PNG, JPG o JPEG.")
        super().clean()

    

class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    nit = models.CharField(max_length=255)
    telefono = models.CharField(max_length=255)
    correo_electronico = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.nombre

# class MateriaPrima(models.Model):
#     nombre = models.CharField(max_length=255)
#     proveedores = models.ForeignKey(Proveedor, on_delete=models.DO_NOTHING)
#     unidad_medida = models.CharField(max_length=50)
#     cantidad = models.IntegerField()
#     fecha_vencimiento = models.DateField(null=True, blank=True)
#     foto = models.ImageField(default=None, upload_to='fotos/fotos_productos/')
#     ultima_actualizacion = models.DateTimeField(auto_now=True)


# class MovimientoStock(models.Model):
#     fecha_movimiento = models.DateTimeField(auto_now_add=True)
#     cantidad_movida = models.IntegerField()
#     estados = (
#         ("1", "Entrada"),
#         ("2", "Salida"),
#         ("3", "Bodega"),
#     )
#     estado = models.CharField(max_length=5, choices=estados, default="1", null=True, blank=True)
#     productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)
#     almacenes = models.ForeignKey(Almacen, on_delete=models.DO_NOTHING)
#     materiaPrima = models.ForeignKey(MateriaPrima, on_delete=models.DO_NOTHING)


# class Receta(models.Model):
#     cantidad_usada = models.IntegerField(null=True, blank=True)
#     materiaPrima = models.ForeignKey(MateriaPrima, on_delete=models.DO_NOTHING)
#     productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)


# class AlertaStock(models.Model):
#     materiaPrima = models.ForeignKey(MateriaPrima, on_delete=models.DO_NOTHING)
#     productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)
#     Nivel_Minimo = models.IntegerField()
#     fecha_vencimiento = models.IntegerField()

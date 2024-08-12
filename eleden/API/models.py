from django.db import models

from .authentication import CustomUserManager

from django.contrib.auth.models import AbstractUser, BaseUserManager

class ventaSoftware(models.Model):
    nombre = models.CharField(max_length=200)
    stock = models.IntegerField()
    precio = models.IntegerField()
    descripcion = models.TextField(help_text="Descripción del producto")
    foto = models.ImageField(upload_to="fotos_paquetes/", default="fotos_paquetes/default.png")

    def subtotal(self):
        return f"${self.stock * self.precio}"

    def __str__(self):
        return f"{self.nombre}"

class Usuario(AbstractUser):
    username = None
    nombreCompleto = models.CharField(max_length=254)
    usuario = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=254)
    ROLES = (
        ("ADMIN", "Administrador"),
        ("SECRE", "Secretaria"),
        ("VENDE", "Vendedor"),
        ("USUAR", "Usuario"),
    )

    rol = models.CharField(max_length=5, choices=ROLES, default="USUAR", null=True, blank=True)
    foto = models.ImageField(upload_to="fotos/", default="fotos/default.png")
    token = models.CharField(max_length=10, null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = "usuario"
    REQUIRED_FIELDS = ["nombreCompleto"]

    def __str__(self):
        return f"{self.nombreCompleto} - {self.rol}"

class Compra(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    ESTADO = (
        (1, "Creado"),
        (2, "Enviado"),
        (3, "Cancelado"),
        )
    estado = models.IntegerField(choices=ESTADO, default=1, blank=True)

    def __str__(self):
        return f"{self.id} - {self.usuario}"


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
    nit = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255)
    correo_electronico = models.EmailField(null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre}"


class ProductoTerminado(models.Model):
    nombre = models.CharField(max_length=255)
    categorias = models.ForeignKey(CategoriaProducto, on_delete=models.DO_NOTHING)
    unidad_medida = models.CharField(max_length=50)
    lote = models.CharField(max_length=50)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    cantidad = models.CharField(max_length=50, null=True)
    precio = models.CharField(max_length=50, null=True)
    foto = models.ImageField(default='fotos/default.png', upload_to='fotos_productos/')

    def __str__(self):
        return self.nombre




class Devolucion(models.Model):
    fecha_devolucion = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=255, null=True, blank=True)
    foto = models.ImageField(default='fotos/default.png', upload_to='fotos/fotos_productos/')
    productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)


class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    nit = models.CharField(max_length=255)
    telefono = models.CharField(max_length=255)
    correo_electronico = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class MateriaPrima(models.Model):
    nombre = models.CharField(max_length=255)
    proveedores = models.ForeignKey(Proveedor, on_delete=models.DO_NOTHING)
    unidad_medida = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    foto = models.ImageField(default=None, upload_to='fotos/fotos_productos/')
    ultima_actualizacion = models.DateTimeField(auto_now=True)


class MovimientoStock(models.Model):
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    cantidad_movida = models.IntegerField()
    estados = (
        ("1", "Entrada"),
        ("2", "Salida"),
        ("3", "Bodega"),
    )
    estado = models.CharField(max_length=5, choices=estados, default="1", null=True, blank=True)
    productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)
    almacenes = models.ForeignKey(Almacen, on_delete=models.DO_NOTHING)
    materiaPrima = models.ForeignKey(MateriaPrima, on_delete=models.DO_NOTHING)


class Receta(models.Model):
    cantidad_usada = models.IntegerField(null=True, blank=True)
    materiaPrima = models.ForeignKey(MateriaPrima, on_delete=models.DO_NOTHING)
    productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)


# class Pedido(models.Model):
#     clientes = models.ForeignKey(Cliente, on_delete=models.DO_NOTHING)
#     fecha_pedido = models.DateField()


# class DetallePedido(models.Model):
#     cantidad = models.IntegerField()
#     precio_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)
#     pedidos = models.ForeignKey(Pedido, on_delete=models.DO_NOTHING)

class Pedido(models.Model):
    clientes = models.ForeignKey(Cliente, on_delete=models.DO_NOTHING)
    productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_pedido = models.DateField()

class AlertaStock(models.Model):
    materiaPrima = models.ForeignKey(MateriaPrima, on_delete=models.DO_NOTHING)
    productos = models.ForeignKey(ProductoTerminado, on_delete=models.DO_NOTHING)
    Nivel_Minimo = models.IntegerField()
    fecha_vencimiento = models.IntegerField()

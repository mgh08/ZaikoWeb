from random import randint

from django import forms
# ---- Agregue esto para generar Token a nuevos usuarios	*******
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.authtoken.models import Token

from django.core.mail import BadHeaderError, EmailMessage
from django.template.loader import render_to_string

from .encriptar import *
from .serializers import *


# Create your views here.


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# ---- Agregue esto para generar Token a nuevos usuarios	*******

# vistas APP
def index(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        return redirect("panelDeGestion")
    else:
        return render(request, "API/index/index.html")


def login(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        clave = request.POST.get("clave")
        try:
            q = Usuario.objects.get(usuario=usuario)
            verify = verify_password(clave, q.password)
            if verify:
                messages.success(request, f"Bienvenido {q.nombreCompleto}")
                # Crear la sesión......
                request.session["logueo"] = {
                    "id": q.id,
                    "nombre": q.nombreCompleto,
                    "rol": q.rol
                }
                request.session["carrito"] = []
                request.session["items_carrito"] = 0

                return redirect("tienda")
            else:
                raise Exception(verify)

        except Exception as e:
            messages.error(request, f"Usuario o contraseña no válidos...{e} ")
            return redirect("index")
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("index")


def recuperar_clave_form(request):
    if request.method == "POST":
        try:
            q = Usuario.objects.get(correo=request.POST.get("correo"))
            num = randint(100000, 999999)
            # convertir num a base64 para ocultarlo un poco
            ofuscado = base64.b64encode(str(num).encode("ascii")).decode("ascii")
            q.token = ofuscado
            q.save()

            # envío de correo
            ruta = reverse(verificar_token_form, args=(q.correo,))

            resultado = enviar_correo(ruta, q.correo, q.token)
            messages.info(request, resultado)
            return redirect("verificar_token_form", correo=q.correo)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no existe...")

        return redirect("recuperar_clave_form")
    else:
        return render(request, "inventario/login/recuperar_clave_form.html")


def verificar_token_form(request, correo):
    if request.method == "POST":
        try:
            q = Usuario.objects.get(correo=correo)
            if q.token != "" and q.token == request.POST.get("token"):
                messages.success(request, "Token OK, cambie su clave!!")
                return redirect("olvide_mi_clave", correo=correo)
            else:
                messages.error(request, "Token no válido...")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no existe...")

        return redirect("verificar_token_form", correo=correo)
    else:
        contexto = {"correo": correo}
        return render(request, "inventario/login/verificar_token_form.html", contexto)


def logout(request):
    logueo = request.session.get("logueo", False)
    if logueo:
        del request.session["logueo"]
        # del request.session["carrito"]
        # del request.session["items_carrito"]
        messages.info(request, "Sesion cerrada correctamente")
        return redirect("index")
    else:
        messages.info(request, "No se pudo cerrar sesión, intente de nuevo")
        return redirect("panelDeGestion")


def handle_uploaded_file(f):
    with open(f"{settings.MEDIA_ROOT}/fotos/{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def panelDeGestion(request):
    return render(request, 'API/panelDeGestion/panelDeGestion.html')


def graficos(request):
    return render(request, 'API/graficos/graficos.html')


def pruebaDemo(request):
    return render(request, 'API/index/pruebaDemo.html')


def invBasico(request):
    return render(request, 'API/paquetes/inventarioBasico.html')


def invAvanzado(request):
    return render(request, 'API/paquetes/inventarioAvanzado.html')


def invPremium(request):
    return render(request, 'API/paquetes/inventarioPremium.html')


def pruebaGratis(request):
    return render(request, 'API/paquetes/pruebaGratis.html')


def clientes(request):
    q = Cliente.objects.all()
    context = {"data": q}
    return render(request, "API/clientes/clientes.html", context)


def buscar(request):
    if request.method == "POST":
        dato = request.POST.get("dato_buscar")
        q = Cliente.objects.filter(Q(nombre__icontains=dato) | Q(correo_electronico=dato))
        contexto = {"data": q}
        return render(request, "API/clientes/clientes.html", contexto)
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("clientes")


def clientes_formulario(request):
    return render(request, 'API/clientes/clientes_formulario.html')


def clientes_guardar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        nit = request.POST.get("nit")
        contacto = request.POST.get("contacto")
        correo_electronico = request.POST.get("correo_electronico")
        direccion = request.POST.get("direccion")
        try:
            q = Cliente(nombre=nombre, nit=nit, contacto=contacto, correo_electronico=correo_electronico,
                        direccion=direccion)
            q.save()
            messages.success(request, "Registro guardado correctamente!!")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("clientes")  # Redirige a la página clientes en caso de error
        return redirect("clientes")  # Redirige a la página clientes después de guardar exitosamente
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("clientes_formulario")


def clientes_formulario_editar(request, id_cliente):
    q = Cliente.objects.get(pk=id_cliente)
    datos = {"registro": q}
    return render(request, "API/clientes/clientes_formulario.html", datos)


def clientes_actualizar(request):
    c = Cliente.objects.get(pk=request.POST.get("id"))
    try:
        c.nombre = request.POST.get("nombre")
        c.nit = request.POST.get("nit")
        c.contacto = request.POST.get("contacto")
        c.correo_electronico = request.POST.get("correo_electronico")
        c.direccion = request.POST.get("direccion")
        c.save()
        messages.success(request, "Registro actualizado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect("clientes")
    return redirect("clientes")


def clientes_eliminar(request, id):
    try:
        q = Cliente.objects.get(pk=id)
        q.delete()
        messages.success(request, "Registro eliminado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("clientes")


# Devoluciones
class DevolucionFormulario(forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = '__all__'


def devoluciones_guardar(request):
    if request.method == 'POST':
        fecha_devolucion = request.POST.get("fecha_devolucion")
        motivo = request.POST.get("motivo")
        foto = request.FILES.get("foto") if request.FILES.get("foto") else 'fotos/default.png'
        nombre_productos = request.POST.get("productos")
        try:
            productos = ProductoTerminado.objects.get(nombre=nombre_productos)
        except ProductoTerminado.DoesNotExist:
            messages.error(request, f"Devolucion {nombre_productos} no encontrado")
            return redirect("registrarDevoluciones")
        try:
            q = Devolucion(fecha_devolucion=fecha_devolucion, motivo=motivo, foto=foto, productos=productos)
            q.save()
            messages.success(request, "Devoluciones guardadas exitosamente...")
        except Exception as e:
            messages.error(request, f"error: {e}")
            # return redirect("registrarDevoluciones")
        return redirect("listarDevoluciones")
    else:
        messages.warning(request, "no se han enviado datos...")
        return redirect("listarDevoluciones")


def listarDevoluciones(request):
    q = Devolucion.objects.all()
    context = {"data": q}
    return render(request, "API/devoluciones/listarDevoluciones.html", context)


def registrar_devoluciones(request):
    return render(request, 'API/devoluciones/registrarDevoluciones.html')


def devoluciones_eliminar(request, id):
    try:
        q = Devolucion.objects.get(id=id)
        q.delete()
        messages.success(request, "Eliminado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("listarDevoluciones")


def devoluciones_editar(request, id):
    q = Devolucion.objects.get(id=id)
    context = {"registro": q}
    return render(request, "API/devoluciones/registrarDevoluciones.html", context)


def devoluciones_actualizar(request):
    id = request.POST.get("id")
    d = Devolucion.objects.get(pk=id)
    try:
        d.fecha_devolucion = request.POST.get("fecha_devolucion")
        d.motivo = request.POST.get("motivo")
        d.foto = request.FILES.get("foto") if request.FILES.get("foto") else None
        nombre_productos = request.POST.get("productos")
        try:
            productos = ProductoTerminado.objects.get(nombre=nombre_productos)
        except ProductoTerminado.DoesNotExist:
            messages.error(request, f"Producto {nombre_productos} no encontrado")
            return redirect("listarDevoluciones")
        d.productos = productos
        d.save()
        messages.success(request, "Actualizado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect("listarDevoluciones")
    return redirect("listarDevoluciones")


# proveedores
# proveedores
def proveedores(request):
    return render(request, 'API/proveedores/proveedores.html')


def registrarProveedores(request):
    q = Devolucion.objects.all()
    context = {"data": q}
    return render(request, "API/proveedores/registrarProveedores.html", context)


def proveedores_guardar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        nit = request.POST.get("nit")
        telefono = request.POST.get("telefono")
        correo_electronico = request.POST.get("correo_electronico")
        try:
            q = Proveedor(nombre=nombre, nit=nit, telefono=telefono, correo_electronico=correo_electronico)
            q.save()
            messages.success(request, "Registro guardado correctamente!!")
        except Exception as e:
            messages.error(request, f"error: {e}")
            return redirect("registrarProveedores")
        return redirect("registrarProveedores")
    else:
        messages.warning(request, "no se han enviado datos...")
        return redirect("registrarProveedores")


def registrarProveedores(request):
    q = Proveedor.objects.all()
    context = {"data": q}
    return render(request, "API/proveedores/registrarProveedores.html", context)


def listarProveedores(request):
    q = Proveedor.objects.all()
    context = {"data": q}
    return render(request, 'API/proveedores/listarProveedores.html', context)


def proveedores_eliminar(request, id):
    try:
        q = Proveedor.objects.get(id=id)
        q.delete()
        messages.success(request, f"Se ha eliminado correctamente {q.nombre}")
    except Exception as e:
        messages.error(request, f"Error {e}")
    return redirect("listarProveedores")


def proveedores_editar(request, id):
    q = Proveedor.objects.get(id=id)
    context = {"registro": q}
    return render(request, "API/proveedores/registrarProveedores.html", context)


def proveedores_actualizar(request):
    p = Proveedor.objects.get(pk=request.POST.get("id"))
    try:
        p.nombre = request.POST.get("nombre")
        p.nit = request.POST.get("nit")
        p.telefono = request.POST.get("telefono")
        p.correo_electronico = request.POST.get("correo_electronico")
        p.save()
        messages.success(request, f"Se ha actualizado correctamente {p.nombre}")

    except Exception as e:
        messages.error(request, f"Error {e}")
        return redirect("listarProveedores")
    return redirect("listarProveedores")


# materia prima


def resgistrarMateriaPrima(request):
    if request.method == 'POST':
        nombre = request.POST.get("nombre")
        nombre_proveedor = request.POST.get("proveedores")
        try:
            proveedores = Proveedor.objects.get(nombre=nombre_proveedor)
        except Proveedor.DoesNotExist:
            messages.error(request, f"Proveedor {nombre_proveedor} no encontrado")
            return redirect("registrarMateriaPrima")
        unidad_medida = request.POST.get("unidad_medida")
        cantidad = request.POST.get("cantidad")
        fecha_vencimiento = request.POST.get("fecha_vencimiento")
        foto = request.FILES.get("foto")
        ultima_actualizacion = request.POST.get("ultima_actualizacion")
        try:
            q = MateriaPrima(nombre=nombre, proveedores=proveedores, unidad_medida=unidad_medida, cantidad=cantidad,
                             fecha_vencimiento=fecha_vencimiento, foto=foto, ultima_actualizacion=ultima_actualizacion)
            q.save()
            messages.success(request, f"Se ha registrado exitosamente  {nombre}")
        except Exception as e:
            messages.error(request, f"error: {e}")
        return redirect("materiaPrima")
    else:
        messages.warning(request, "No se han enviado datos...")
        return redirect("registrarMateriaPrima")


def registrarMateriaPrima(request):
    q = MateriaPrima.objects.all()
    context = {"data": q}
    return render(request, "API/materiaPrima/registrarMateriaPrima.html", context)


def materiaPrima(request):
    q = MateriaPrima.objects.all()
    context = {"data": q}
    return render(request, 'API/materiaPrima/materiaPrima.html', context)


def materia_prima_editar(request, id):
    q = MateriaPrima.objects.get(id=id)
    context = {"registro": q}
    return render(request, "API/materiaPrima/registrarMateriaPrima.html", context)


def materia_prima_actualizar(request):
    m = MateriaPrima.objects.get(pk=request.POST.get("id"))
    try:
        m.nombre = request.POST.get("nombre")
        m.Proveedor = request.POST.get("proveedores")
        m.unidad_medida = request.POST.get("unidad_medida")
        m.cantidad = request.POST.get("cantidad")
        m.fecha_vencimiento = request.POST.get("fecha_vencimiento")
        m.foto = request.FILES.get("foto")
        m.ultima_actualizacion = request.POST.get("ultima_actualizacion")
        m.save()
        messages.success(request, f"Se ha actualizado correctamente {m.nombre}")
    except Exception as e:
        messages.error(request, f"Error {e}")
        return redirect("materiaPrima")
    return redirect("materiaPrima")


def materia_prima_eliminar(request, id):
    try:
        q = MateriaPrima.objects.get(id=id)
        q.delete()
        messages.success(request, f"Se ha eliminado correctamente {q.nombre}")
    except Exception as e:
        messages.error(request, f"Error {e}")
    return redirect("materiaPrima")


# miguel
def productoTerminado(request):
    q = ProductoTerminado.objects.all()
    context = {"data": q}
    return render(request, "API/productos/productoTerminado.html", context)


def ver_productos(request, id):
    p = ProductoTerminado.objects.get(pk=id)
    try:
        p.nombre = request.POST.get("nombre")
        p.unidad_medida = request.POST.get("unidad_medida")
        p.cantidad = request.POST.get("cantidad")
        p.categorias = CategoriaProducto.objects.get(pk=request.POST.get("categorias"))
        p.lote = request.POST.get("lote")
        p.fecha_vencimiento = request.POST.get("fecha_vencimiento")
        p.precio = request.POST.get("precio")
        p.foto = request.FILES.get("foto")
        context = {"data": p}
        return redirect("productoTerminado", context)
    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect("productoTerminado")


def registrar_producto(request):
    q = CategoriaProducto.objects.all()
    context = {"categorias": q}
    return render(request, "API/productos/registrar_producto.html", context)


def buscar_productos(request):
    if request.method == "POST":
        dato = request.POST.get("productos_buscar")
        q = ProductoTerminado.objects.filter(Q(nombre__icontains=dato))
        contexto = {"data": q}
        return render(request, "API/productos/productoTerminado.html", contexto)
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("productoTerminado")


def productos_eliminar(request, id):
    try:
        q = ProductoTerminado.objects.get(pk=id)
        q.delete()
        messages.success(request, "Registro eliminado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("productoTerminado")


def productos_guardar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        unidad_medida = request.POST.get("unidad_medida")
        cantidad = request.POST.get("cantidad")
        categorias = CategoriaProducto.objects.get(pk=request.POST.get("categorias"))
        lote = request.POST.get("lote")
        fecha_vencimiento = request.POST.get("fecha_vencimiento")
        precio = request.POST.get("precio")
        foto = request.FILES.get("foto")
        try:
            q = ProductoTerminado(
                nombre=nombre,
                unidad_medida=unidad_medida,
                cantidad=cantidad,
                categorias=categorias,
                lote=lote,
                fecha_vencimiento=fecha_vencimiento,
                precio=precio,
                foto=foto
            )
            q.save()
            messages.success(request, "Registro guardado correctamente!!")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            # Redirige a la página clientes en caso de error
        return redirect("productoTerminado")  # Redirige a la página clientes después de guardar exitosamente
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("productoTerminado")


# R


def productos_actualizar(request, id):
    p = ProductoTerminado.objects.get(pk=id)
    try:
        foto = request.FILES.get("foto")
        if foto is None:
            foto = p.foto
        p.foto = foto
        p.nombre = request.POST.get("nombre")
        p.unidad_medida = request.POST.get("unidad_medida")
        p.cantidad = request.POST.get("cantidad")
        p.categorias = CategoriaProducto.objects.get(pk=request.POST.get("categorias"))
        p.lote = request.POST.get("lote")
        p.fecha_vencimiento = request.POST.get("fecha_vencimiento")
        p.precio = request.POST.get("precio")

        p.save()
        messages.success(request, "Registro actualizado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect("productoTerminado")
    return redirect("productoTerminado")


def productos_formulario_editar(request, id):
    query_productos = ProductoTerminado.objects.get(pk=id)
    query_categorias = CategoriaProducto.objects.all()

    contexto = {"registro": query_productos, "categorias": query_categorias}
    return render(request, "API/productos/registrar_producto.html", contexto)


# def productos_formulario_editar(request, id):
#     q = ProductoTerminado.objects.get(pk=id)
#     datos = {"registro": q}
#     return render(request, "API/productos/registrar_producto.html", datos)


# R

def enviarCorreo(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        subject = request.POST["subject"]
        message = request.POST["message"]

        template = render_to_string('API/email/email_template.html', {
            'name': name,
            'email': email,
            'message': message
        })

        email = EmailMessage(
            subject,
            template,
            settings.EMAIL_HOST_USER,
            ['juanr7788@gmail.com']
        )

        email.fail_silently = False
        email.send()

        messages.success(request, 'Se ha enviado tu solicitud.')
        return redirect('index')

    # destinatario = "jor.sincelejo@gmail.com"
    # mensaje = """


# 		<h1 style='color:blue;'>Tienda virtual</h1>
# 		<p>Su pedido está listo y en estado "creado".</p>
# 		<p>Tienda ADSO, 2024</p>
# 		<br>
# 		<a href='http://127.0.0.1:8000/inventario/'>Recuperar contraseña </a>
# 		"""

# try:
#     msg = EmailMessage("Tienda ADSO", mensaje, settings.EMAIL_HOST_USER, [destinatario])
#     msg.content_subtype = "html"  # Habilitar contenido html
#     msg.send()
#     return HttpResponse("Correo enviado")
# except BadHeaderError:
#     return HttpResponse("Encabezado no válido")
# except Exception as e:
#     return HttpResponse(f"Error: {e}")


# categorias

def categorias(request):
    q = CategoriaProducto.objects.all()
    context = {"data": q}
    return render(request, "API/categorias/categorias_listar.html", context)


def categorias_formulario(request):
    return render(request, "API/categorias/categorias_formulario.html")


def categorias_guardar(request):
    if request.method == "POST":
        nombre_categoria = request.POST.get("nombre_categoria")
        descripcion = request.POST.get("descripcion")
        try:
            q = CategoriaProducto(nombre_categoria=nombre_categoria, descripcion=descripcion)
            q.save()
            messages.success(request, "Registro guardado correctamente!!")
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect("categorias")
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("categorias_formulario")


def categorias_eliminar(request, id):
    try:
        q = CategoriaProducto.objects.get(pk=id)
        q.delete()
        messages.success(request, "Registro eliminado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("categorias")


def categorias_formulario_editar(request, id):
    q = CategoriaProducto.objects.get(pk=id)
    datos = {"registro": q}
    return render(request, "API/categorias/categorias_formulario.html", datos)


def categorias_actualizar(request):
    c = CategoriaProducto.objects.get(pk=request.POST.get("id"))
    try:
        c.nombre_categoria = request.POST.get("nombre_categoria")
        c.descripcion = request.POST.get("descripcion")
        c.save()
        messages.success(request, "Registro actualizado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("categorias")


def buscar_categorias(request):
    if request.method == "POST":
        dato = request.POST.get("buscar_categorias")
        q = CategoriaProducto.objects.filter(Q(nombre_categoria__icontains=dato) | Q(descripcion__icontains=dato))
        contexto = {"data": q}
        return render(request, "API/categorias/categorias_listar.html", contexto)
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("categorias")


def handle_uploaded_file(f):
    with open(f"{settings.MEDIA_ROOT}/fotos/{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def registrarse(request):
    if request.method == 'POST':
        if request.POST.get("clave1") == request.POST.get("clave2"):
            foto = request.FILES.get("foto")
            if foto is not None:
                handle_uploaded_file(foto)
                foto = f"fotos/{foto.name}"
            else:
                foto = "fotos/default.png"

            clave = hash_password(request.POST.get("clave1"))
            print("Creamos instancia")
            q = Usuario(
                nombreCompleto=request.POST.get("nombreCompleto"),
                usuario=request.POST.get("usuario"),
                password=clave,
                foto=foto
            )
            q.save()
            messages.success(request, "Registro correcto!!!!")
            # logueo automatico
            request.session["logueo"] = {
                "id": q.id,
                "nombre": q.nombreCompleto,
                "rol": q.rol
            }
            return redirect("panelDeGestion")
        else:
            messages.warning(request, "No coincíden las contraseñas")
            return redirect("index")
    else:
        return render(request, "API/index/index.html")


# Carrito

def ver_carrito(request):
    carrito = request.session.get("carrito", [])

    total = 0
    productos = []
    for p in carrito:
        q = ventaSoftware.objects.get(pk=p["id"])
        q.cantidad = p["cantidad"]
        q.subtotal = int(p["cantidad"]) * q.precio
        productos.append(q)
        total += int(q.subtotal)

    contexto = {"data": productos, "total": total}
    return render(request, "API/carrito/carrito.html", contexto)


def eliminar_item_carrito(request, id_producto):
    carrito = request.session.get("carrito", False)
    for i, p in enumerate(carrito):
        if id_producto == int(p["id"]):
            carrito.pop(i)
            messages.info(request, "Producto eliminado...")
            break
    else:
        messages.warning(request, "Producto no encontrado...")

    request.session["carrito"] = carrito
    request.session["items_carrito"] = len(carrito)
    return redirect("ver_carrito")


@transaction.atomic
def guardar_compra(request):
    carrito = request.session.get("carrito", False)

    # capturo variable de sesión para averiguar ID de usuario
    logueo = request.session.get("logueo", False)
    u = Usuario.objects.get(pk=logueo["id"])
    # import traceback
    try:
        c = Compra(usuario=u)
        c.save()
        print(f"Id compra: {c.id}")

        for p in carrito:
            try:
                pro = ventaSoftware.objects.get(pk=p["id"])
            except ventaSoftware.DoesNotExist:
                raise Exception(f"No se pudo realizar la compra, El producto {pro} ya no existe..")

            if pro.stock >= p["cantidad"]:
                dc = DetalleCompra(
                    id_compra=c,
                    producto=pro,
                    cantidad=int(p["cantidad"]),
                    precio=pro.precio
                )
                dc.save()
                # disminuir inventario
                pro.stock -= int(p["cantidad"])
                pro.save()
            else:
                raise Exception(f"El producto {pro} no tiene suficiente inventario...")

        # vaciar carrito e items en cero.
        request.session["carrito"] = []
        request.session["items_carrito"] = 0

        messages.success(request, "Compra guardada correctamente!!")
    except Exception as e:
        # ************* si ERROR **********
        transaction.set_rollback(True)
        # rollback
        messages.warning(request, f"Error: {e}")  # - {traceback.format_exc()}

    return redirect("tienda")


def vaciar_carrito(request):
    carrito = request.session.get("carrito", False)
    try:
        # vaciar lista....
        carrito.clear()

        request.session["carrito"] = carrito
        request.session["items_carrito"] = 0
        messages.success(request, "Ya no hay items en el carrito!!")
    except Exception as e:
        messages.error(request, "Ocurrió un error, intente de nuevo...")

    return redirect("tienda")


def carrito_add(request):
    if request.method == "GET":
        id_producto = request.GET.get("id_producto")
        cantidad = int(request.GET.get("cantidad"))
        q = ventaSoftware.objects.get(pk=id_producto)
        carrito = request.session.get("carrito", [])
        if not isinstance(carrito, list):
            carrito = []
            request.session["carrito"] = carrito
            request.session["items_carrito"] = 0

        for p in carrito:
            if id_producto == p["id"]:
                p["cantidad"] += cantidad
                messages.info(request, "Producto ya existe, cantidad actualizada")
                break
        else:
            carrito.append({"id": id_producto, "cantidad": cantidad})
            messages.success(request, "Producto agregado correctamente!!")

        request.session["carrito"] = carrito
        request.session["items_carrito"] = len(carrito)

        return redirect("ver_carrito")
    else:
        return HttpResponse("No se enviaron datos...")


def productos_listar_software(request):
    logueo = request.session.get("logueo", False)

    if logueo and (logueo["rol"] == "ADMIN"):
        q = ventaSoftware.objects.all()
        context = {"data": q}
        return render(request, "API/carrito/listarSoftware/listarSoftware.html", context)
    else:
        messages.info(request, "No tiene permisos para acceder al módulo...")
        return redirect("index")


def productos_guardar_software(request):
    if request.method == "POST":
        foto = request.FILES.get("foto")
        if foto is None:
            foto = "fotos_paquetes/default.png"
        nombre = request.POST.get("nombre")
        stock = request.POST.get("stock")
        descripcion = request.POST.get("descripcion")
        precio = request.POST.get("precio")
        try:
            q = ventaSoftware(foto=foto, nombre=nombre, stock=stock, descripcion=descripcion, precio=precio)
            q.save()
            messages.success(request, "Registro guardado correctamente!!")
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect("productos_listar_software")
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("productos_formulario")


def productos_actualizar_software(request):
    p = ventaSoftware.objects.get(pk=request.POST.get("id"))
    try:
        foto = request.FILES.get("foto")
        if foto is None:
            foto = p.foto
        p.foto = foto
        p.nombre = request.POST.get("nombre")
        p.stock = request.POST.get("stock")
        p.precio = request.POST.get("precio")
        p.save()
        messages.success(request, "Registro actualizado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("productos_listar_software")


def productos_editar_software(request, id_producto):
    query_productos = ventaSoftware.objects.get(pk=id_producto)

    contexto = {"registro": query_productos}
    return render(request, "API/carrito/editarSoftware/editarSoftware.html", contexto)


def productos_eliminar_software(request, id_producto):
    try:
        q = ventaSoftware.objects.get(pk=id_producto)
        q.delete()
        messages.success(request, "Registro eliminado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("productos_listar_software")


def productos_formulario_software(request):
    q = ventaSoftware.objects.all()
    context = {"data": q}
    return render(request, "API/carrito/editarSoftware/editarSoftware.html", context)


def tienda(request):
    # logueo = request.session.get("logueo", False)
    logueo = True
    if logueo:
        p = ventaSoftware.objects.all()
        contexto = {"data": p}
        return render(request, 'API/carrito/tienda.html', contexto)
    else:
        return redirect("index")


# ------------------------------- Para los permisos de los end-points -----------------------------
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['username']
        # traer datos del usuario para bienvenida y ROL
        usuario = Usuario.objects.get(usuario=user)
        token, created = Token.objects.get_or_create(user=usuario)

        return Response({
            'token': token.key,
            'user': {
                'user_id': usuario.pk,
                'usuario': usuario.usuario,
                'nombre_completo': usuario.nombreCompleto,
                'rol': usuario.rol,
                'foto': usuario.foto.url
            }
        })

def auditoria(request):
    return render(request, 'API/auditoria/auditoria.html')

class AlmacenViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer


class AlertaStockViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AlertaStock.objects.all()
    serializer_class = AlertaStockSerializer


class CategoriaProductoViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


class DevolucionViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Devolucion.objects.all()
    serializer_class = DevolucionSerializer


class MateriaPrimaViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = MateriaPrima.objects.all()
    serializer_class = MateriaPrimaSerializer


class MovimientoStockViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = MovimientoStock.objects.all()
    serializer_class = MovimientoStockSerializer


class ProductoTerminadoViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = ProductoTerminado.objects.all()
    serializer_class = ProductoTerminadoSerializer


class ProveedorViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class RecetaViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer


class DetallePedidoViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer


class AlertaStockViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AlertaStock.objects.all()
    serializer_class = AlertaStockSerializer


class ventaSoftwareViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ventaSoftware.objects.all()
    serializer_class = ventaSoftwareSerializer
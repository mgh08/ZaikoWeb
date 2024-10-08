from random import randint

from django import forms
# ---- Agregue esto para generar Token a nuevos usuarios	*******
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.authtoken.models import Token

from django.core.mail import BadHeaderError, EmailMessage
from django.template.loader import render_to_string

from .encriptar import *
from .serializers import *
from django.contrib.auth import authenticate, login as django_login

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
                request.session["logueo"] = {
                    "id": q.id,
                    "nombre": q.nombreCompleto,
                    "rol": q.rol
                }
                request.session["carrito"] = []
                request.session["items_carrito"] = 0
                messages.success(request, f"Bienvenido {q.nombreCompleto}")
                return redirect("tienda")
            else:
                messages.error(request, "Contraseña incorrecta.")
                return redirect("index")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect("index")
    else:
        messages.warning(request, "No se enviaron datos.")
        return redirect("index")



def recuperar_clave_form(request):
    if request.method == "POST":
        try:
            q = Usuario.objects.get(usuario=request.POST.get("correo"))
            num = randint(100000, 999999)
            ofuscado = base64.b64encode(str(num).encode("ascii")).decode("ascii")
            q.token = ofuscado
            q.save()
            ruta = request.build_absolute_uri(reverse("verificar_token_form", args=[q.usuario]))
            resultado = enviarCorreo(q.usuario, q.token, ruta)
            messages.info(request, resultado)
            return redirect("verificar_token_form", correo=q.usuario)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect("recuperar_clave_form")
    return render(request, "API/index/recuperar_clave_form.html")


def verificar_token_form(request, correo):
    if request.method == "POST":
        try:
            q = Usuario.objects.get(usuario=correo)
            if q.token != "" and q.token == request.POST.get("token"):
                messages.success(request, "Token OK, cambie su clave!!")
                return redirect("olvide_mi_clave", correo=correo)
            else:
                messages.error(request, "Token no válido...")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no existe...")
        return redirect("verificar_token_form", correo=correo)
    else:
        contexto = {"usuario": correo}
        return render(request, "API/index/verificar_token_form.html", contexto)

 


def olvide_mi_clave(request, correo):
    if request.method == "POST":
        c_nueva1 = request.POST.get("nueva1")
        c_nueva2 = request.POST.get("nueva2")
        try:
            q = Usuario.objects.get(usuario=correo)
            if c_nueva1 == c_nueva2:
                q.set_password(c_nueva1)
                q.token = ""  # Borrar el token
                q.save()
                messages.success(request, "Clave cambiada correctamente.")
                return redirect("index")
            else:
                messages.warning(request, "Las contraseñas no coinciden.")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
        return redirect("olvide_mi_clave", correo=correo)
    return render(request, "API/index/olvide_mi_clave.html", {"correo": correo})



from django.contrib.auth import logout as django_logout

def logout(request):
    django_logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("index")




def handle_uploaded_file(f):
    with open(f"{settings.MEDIA_ROOT}/fotos/{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def formulario_cambiar_clave(request):
    logueo = request.session.get("logueo", True)
    if logueo:
        return render(request, "API/index/formulario_cambiar_clave.html")
    else:
        messages.info



def cambiar_clave(request):
    if request.method == "POST":
        c_actual = request.POST.get("actual")
        c_nueva1 = request.POST.get("nueva1")
        c_nueva2 = request.POST.get("nueva2")

        logueo = request.session.get("logueo", False)

        if logueo:
            try:
                q = Usuario.objects.get(pk=logueo["id"])

                # Verificar la contraseña actual
                if q.check_password(c_actual):
                    if c_nueva1 == c_nueva2:
                        q.set_password(c_nueva1)
                        q.save()

                        messages.success(request, "Contraseña cambiada correctamente.")
                    else:
                        messages.warning(request, "Las nuevas contraseñas no coinciden.")
                else:
                    messages.error(request, "La contraseña actual es incorrecta.")
            except Usuario.DoesNotExist:
                messages.error(request, "Usuario no encontrado.")
        return redirect("formulario_cambiar_clave")
    
    return HttpResponse("No se enviaron datos.")


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


# Función para listar los clientes
from django.core.paginator import Paginator

def clientes(request):
    q = Cliente.objects.all()
    
    # Paginación para mejorar el rendimiento y la experiencia del usuario
    paginator = Paginator(q, 10)  # 10 clientes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {"data": page_obj}
    return render(request, "API/clientes/clientes.html", context)


import re

def buscar(request):
    if request.method == "POST":
        dato = request.POST.get("dato_buscar")
        
        if not dato:
            messages.warning(request, "Por favor ingrese un dato para buscar.")
            return redirect("clientes")
        
        # Expresión regular para evitar caracteres no permitidos (por ejemplo, inyección SQL)
        if not re.match(r'^[a-zA-Z0-9@.\s]*$', dato):
            messages.error(request, "El dato de búsqueda contiene caracteres no permitidos.")
            return redirect("clientes")

        q = Cliente.objects.filter(Q(nombre__icontains=dato) | Q(correo_electronico__icontains=dato))
        contexto = {"data": q}
        return render(request, "API/clientes/clientes.html", contexto)
    
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("clientes")


# Función para mostrar el formulario de creación de cliente
def clientes_formulario(request):
    return render(request, 'API/clientes/clientes_formulario.html')

# Función para guardar un nuevo cliente
from django.core.validators import validate_email

def clientes_guardar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        nit = request.POST.get("nit")
        contacto = request.POST.get("contacto")
        correo_electronico = request.POST.get("correo_electronico")
        direccion = request.POST.get("direccion")

        # Validaciones básicas
        if not nombre or not nit or not contacto:
            messages.error(request, "Los campos nombre, NIT y contacto son obligatorios.")
            return redirect("clientes_formulario")

        # Validar NIT único
        if Cliente.objects.filter(nit=nit).exists():
            messages.error(request, "El NIT ya está registrado. Ingrese un NIT único.")
            return redirect("clientes_formulario")

        # Validar correo electrónico
        if correo_electronico:
            try:
                validate_email(correo_electronico)
            except ValidationError:
                messages.error(request, "Correo electrónico inválido.")
                return redirect("clientes_formulario")

        try:
            q = Cliente(nombre=nombre, nit=nit, contacto=contacto, correo_electronico=correo_electronico,
                        direccion=direccion)
            q.save()
            messages.success(request, "Registro guardado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")
            return redirect("clientes_formulario")

        return redirect("clientes")

    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("clientes_formulario")


# Función para mostrar el formulario de edición
def clientes_formulario_editar(request, id_cliente):
    q = get_object_or_404(Cliente, pk=id_cliente)
    datos = {"registro": q}
    return render(request, "API/clientes/clientes_formulario.html", datos)

# Función para actualizar un cliente
def clientes_actualizar(request):
    if request.method == "POST":
        try:
            c = Cliente.objects.get(pk=request.POST.get("id"))
            
            nuevo_nit = request.POST.get("nit")
            
            # Validar que el NIT actualizado sea único, pero permitiendo el NIT actual del cliente
            if Cliente.objects.filter(nit=nuevo_nit).exclude(pk=c.pk).exists():
                messages.error(request, "El NIT ya está registrado.")
                return redirect("clientes_formulario_editar", id_cliente=c.pk)
            
            # Validar correo electrónico
            correo_electronico = request.POST.get("correo_electronico")
            if correo_electronico:
                try:
                    validate_email(correo_electronico)
                except ValidationError:
                    messages.error(request, "Correo electrónico inválido.")
                    return redirect("clientes_formulario_editar", id_cliente=c.pk)

            c.nombre = request.POST.get("nombre")
            c.nit = nuevo_nit
            c.contacto = request.POST.get("contacto")
            c.correo_electronico = correo_electronico
            c.direccion = request.POST.get("direccion")
            c.save()
            
            messages.success(request, "Registro actualizado correctamente!!")
        except Cliente.DoesNotExist:
            messages.error(request, "El cliente no existe.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        
        return redirect("clientes")


# Función para eliminar un cliente
def clientes_eliminar(request, id):
    try:
        cliente = Cliente.objects.get(pk=id)
        if Pedido.objects.filter(clientes=cliente).exists():  # Corregido 'cliente' por 'clientes'
            messages.error(request, "No se puede eliminar el cliente porque tiene pedidos asociados.")
        else:
            cliente.delete()
            messages.success(request, "Cliente eliminado correctamente.")
    except Cliente.DoesNotExist:
        messages.error(request, "El cliente no existe.")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {e}")

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
        
        # Validar campos obligatorios
        if not motivo or not nombre_productos:
            messages.error(request, "El motivo y el producto son campos obligatorios.")
            return redirect("registrar_devoluciones")

        # Validar que el producto exista
        try:
            productos = ProductoTerminado.objects.get(nombre=nombre_productos)
        except ProductoTerminado.DoesNotExist:
            messages.error(request, f"El producto {nombre_productos} no fue encontrado.")
            return redirect("registrar_devoluciones")

        # Validar el formato de la imagen
        if foto and not foto.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            messages.error(request, "Solo se permiten imágenes en formato PNG, JPG o JPEG.")
            return redirect("registrar_devoluciones")

        # Guardar la devolución
        try:
            devolucion = Devolucion(fecha_devolucion=fecha_devolucion, motivo=motivo, foto=foto, productos=productos)
            devolucion.save()
            messages.success(request, "Devoluciones guardadas exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar la devolución: {e}")
            return redirect("registrar_devoluciones")

        return redirect("listarDevoluciones")
    else:
        messages.warning(request, "No se han enviado datos...")
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
    try:
        devolucion = Devolucion.objects.get(pk=id)
        motivo = request.POST.get("motivo")
        foto = request.FILES.get("foto") if request.FILES.get("foto") else devolucion.foto
        nombre_productos = request.POST.get("productos")
        
        # Validar campos obligatorios
        if not motivo or not nombre_productos:
            messages.error(request, "El motivo y el producto son campos obligatorios.")
            return redirect(f"devoluciones_editar/{id}/")
        
        # Validar que el producto exista
        try:
            productos = ProductoTerminado.objects.get(nombre=nombre_productos)
        except ProductoTerminado.DoesNotExist:
            messages.error(request, f"El producto {nombre_productos} no fue encontrado.")
            return redirect(f"devoluciones_editar/{id}/")
        
        # Validar el formato de la imagen
        if foto and not foto.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            messages.error(request, "Solo se permiten imágenes en formato PNG, JPG o JPEG.")
            return redirect(f"devoluciones_editar/{id}/")
        
        # Actualizar la devolución
        devolucion.motivo = motivo
        devolucion.foto = foto
        devolucion.productos = productos
        devolucion.save()
        messages.success(request, "Actualizado correctamente!!")
    except Devolucion.DoesNotExist:
        messages.error(request, "La devolución no existe.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("listarDevoluciones")


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


# def registrarMateriaPrima(request):
#     q = MateriaPrima.objects.all()
#     context = {"data": q}
#     return render(request, "API/materiaPrima/registrarMateriaPrima.html", context)


# def materiaPrima(request):
#     q = MateriaPrima.objects.all()
#     context = {"data": q}
#     return render(request, 'API/materiaPrima/materiaPrima.html', context)


# def materia_prima_editar(request, id):
#     q = MateriaPrima.objects.get(id=id)
#     context = {"registro": q}
#     return render(request, "API/materiaPrima/registrarMateriaPrima.html", context)


# def materia_prima_actualizar(request):
#     m = MateriaPrima.objects.get(pk=request.POST.get("id"))
#     try:
#         m.nombre = request.POST.get("nombre")
#         m.Proveedor = request.POST.get("proveedores")
#         m.unidad_medida = request.POST.get("unidad_medida")
#         m.cantidad = request.POST.get("cantidad")
#         m.fecha_vencimiento = request.POST.get("fecha_vencimiento")
#         m.foto = request.FILES.get("foto")
#         m.ultima_actualizacion = request.POST.get("ultima_actualizacion")
#         m.save()
#         messages.success(request, f"Se ha actualizado correctamente {m.nombre}")
#     except Exception as e:
#         messages.error(request, f"Error {e}")
#         return redirect("materiaPrima")
#     return redirect("materiaPrima")


# def materia_prima_eliminar(request, id):
#     try:
#         q = MateriaPrima.objects.get(id=id)
#         q.delete()
#         messages.success(request, f"Se ha eliminado correctamente {q.nombre}")
#     except Exception as e:
#         messages.error(request, f"Error {e}")
#     return redirect("materiaPrima")


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
        # messages.warning(request, "No se enviaron datos...")
        return redirect("productoTerminado")


def productos_eliminar(request, id):
    try:
        q = ProductoTerminado.objects.get(pk=id)
        q.delete()
        messages.success(request, "Registro eliminado correctamente!!")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("productoTerminado")


from django.shortcuts import render, redirect
from django.contrib import messages

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
            q.full_clean()  # Esto activará las validaciones definidas
            q.save()
            messages.success(request, "Registro guardado correctamente!!")
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('registrar_producto')  # Redirige al formulario para corregir errores
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return redirect("productoTerminado")



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



def enviarCorreo(usuario, token, ruta):
    # Aquí se define el asunto del correo
    subject = "Recuperación de contraseña"

    # Renderizamos la plantilla del correo con la información del usuario, token y ruta
    template = render_to_string('API/email/email_template.html', {
        'usuario': usuario,
        'token': token,
        'ruta': ruta
    })

    # Configuramos el correo electrónico
    email = EmailMessage(
        subject,
        template,
        settings.EMAIL_HOST_USER,
        [usuario]  # Aquí usamos el email del usuario
    )

    # Enviamos el correo
    email.fail_silently = False
    email.send()
    
    return "Correo enviado exitosamente"



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


#Pedidos

def pedidos(request, pk=None):
    if pk:
        registro = get_object_or_404(Pedido, pk=pk)
    else:
        registro = None

    clientes = Cliente.objects.all()
    productos = ProductoTerminado.objects.all()
    
    context = {
        'registro': registro,
        'clientes': clientes,
        'productos': productos,
    }
    return render(request, 'pedidos_listar.html', context)

def pedidos_listar(request):
    q = Pedido.objects.all()
    context = {"data": q}
    return render(request, 'API/pedidos/pedidos_listar.html', context)

def pedidos_formulario(request):
    return render(request, "API/pedidos/pedidos_formulario.html")

def pedidos_guardar(request):
    if request.method == "POST":
        cliente_nombre = request.POST.get("clientes")
        cantidad = request.POST.get("cantidad")
        precio_unitario = request.POST.get("precio_unitario")
        fecha_pedido = request.POST.get("fecha_pedido")
        producto_nombre = request.POST.get("productos")
        
        try:
            cliente = Cliente.objects.get(nombre=cliente_nombre)
        except Cliente.DoesNotExist:
            messages.error(request, f"Cliente con nombre '{cliente_nombre}' no encontrado")
            return redirect("pedidos_formulario")
        
        try:
            producto = ProductoTerminado.objects.get(nombre=producto_nombre)
        except ProductoTerminado.DoesNotExist:
            messages.error(request, f"Producto con nombre '{producto_nombre}' no encontrado")
            return redirect("pedidos_formulario")
        
        try:
            cantidad = int(cantidad)
            precio_unitario = float(precio_unitario)
            precio_total = cantidad * precio_unitario
            
            pedido = Pedido(
                clientes=cliente,
                productos=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                precio_total=precio_total,
                fecha_pedido=fecha_pedido
            )
            pedido.save()
            messages.success(request, "Pedido guardado correctamente!!")
            return redirect("pedidos_listar")
        except Exception as e:
            messages.error(request, f"Error al guardar el pedido: {e}")
            return redirect("pedidos_formulario")
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("pedidos_formulario")


def pedidos_formulario_editar(request, id):
    pedido = get_object_or_404(Pedido, pk=id)
    context = {"registro": pedido}
    return render(request, "API/pedidos/pedidos_formulario.html", context)


def pedidos_actualizar(request):
    if request.method == "POST":
        id = request.POST.get("id")
        pedido = get_object_or_404(Pedido, pk=id)       
        try:
            cantidad = request.POST.get("cantidad")
            precio_unitario = request.POST.get("precio_unitario")
            fecha_pedido = request.POST.get("fecha_pedido")
            nombre_cliente = request.POST.get("clientes")
            nombre_producto = request.POST.get("productos")
            
            try:
                cliente = Cliente.objects.get(nombre=nombre_cliente)
            except Cliente.DoesNotExist:
                messages.error(request, f"Cliente con nombre '{nombre_cliente}' no encontrado")
                return redirect("pedidos_formulario")
            
            try:
                producto = ProductoTerminado.objects.get(nombre=nombre_producto)
            except ProductoTerminado.DoesNotExist:
                messages.error(request, f"Producto con nombre '{nombre_producto}' no encontrado")
                return redirect("pedidos_formulario")
            
            pedido.clientes = cliente
            pedido.productos = producto
            pedido.cantidad = int(cantidad)
            pedido.precio_unitario = float(precio_unitario)
            pedido.precio_total = pedido.cantidad * pedido.precio_unitario
            pedido.fecha_pedido = fecha_pedido
            pedido.save()
            
            messages.success(request, "Pedido actualizado correctamente!!")
        except Exception as e:
            messages.error(request, f"Error al actualizar el pedido: {e}")
            return redirect("pedidos_formulario")
        
        return redirect("pedidos_listar")
    else:
        messages.warning(request, "No se enviaron datos...")
        return redirect("pedidos_formulario")


def pedidos_eliminar(request, id):
    try:
        q = Pedido.objects.get(id=id)
        q.delete()
        messages.success(request, f"Se ha eliminado correctamente {q.productos}")
    except Exception as e:
        messages.error(request, f"Error {e}")
    return redirect("pedidos_listar")



#---------------------------------------------

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
    
from django.contrib.auth.decorators import login_required

# Carrito

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseNotAllowed, JsonResponse
from .models import VentaSoftware

# def carrito_add(request, producto_id):
#     if request.method == 'POST':
#         # Lógica para agregar el producto al carrito
#         cantidad = int(request.POST.get('cantidad', 1))
#         producto = get_object_or_404(VentaSoftware, id=producto_id)

#         # Validaciones
#         if cantidad <= 0:
#             messages.error(request, "La cantidad debe ser mayor a cero.")
#             return redirect('tienda')

#         if producto.stock < cantidad:
#             messages.error(request, f"Solo quedan {producto.stock} unidades disponibles.")
#             return redirect('tienda')

#         # Agregar al carrito en la sesión
#         carrito = request.session.get('carrito', {})
#         if producto_id in carrito:
#             carrito[producto_id]['cantidad'] += cantidad  # Incrementar la cantidad
#         else:
#             carrito[producto_id] = {
#                 'nombre': producto.nombre,
#                 'precio': producto.precio,
#                 'cantidad': cantidad,
#                 'subtotal': producto.precio * cantidad  # Calcular subtotal
#             }

#         # Guardar el carrito en la sesión
#         request.session['carrito'] = carrito
#         request.session['items_carrito'] = sum(item['cantidad'] for item in carrito.values())  # Actualizar conteo de items

#         messages.success(request, f"{producto.nombre} agregado al carrito.")
#         return redirect('tienda')  # Redirigir a la tienda

#     # Si no es una solicitud POST, devolver un error 405 (Método no permitido)
#     return HttpResponseNotAllowed(['POST'])

def carrito_add(request, producto_id):
    if request.method == 'POST':  # Solo permitir POST
        # Obtener la cantidad del formulario o la solicitud
        cantidad = int(request.POST.get('cantidad', 1))

        # Obtener el producto
        producto = get_object_or_404(VentaSoftware, id=producto_id)

        # Validar la cantidad y stock
        if cantidad <= 0 or producto.stock < cantidad:
            return JsonResponse({"error": "Cantidad no válida o stock insuficiente"}, status=400)

        # Agregar al carrito (a la sesión del usuario)
        carrito = request.session.get('carrito', {})
        if producto_id in carrito:
            carrito[producto_id]['cantidad'] += cantidad
        else:
            carrito[producto_id] = {
                'nombre': producto.nombre,
                'precio': producto.precio,
                'cantidad': cantidad
            }
        request.session['carrito'] = carrito
        return JsonResponse({"mensaje": "Producto agregado al carrito"})

    return HttpResponseNotAllowed(['POST'])  # Si no es POST, devolver error 405


def ver_carrito(request):
    carrito = request.session.get("carrito", {})
    productos = []
    total = 0

    # Verifica si el carrito no está vacío
    if not carrito:
        messages.info(request, "Tu carrito está vacío.")
        return render(request, 'API/carrito/carrito.html', {'data': productos, 'total': total})

    for id_producto, item in carrito.items():
        try:
            # Intenta obtener el producto
            producto = VentaSoftware.objects.get(pk=id_producto)
            producto.cantidad = item['cantidad']
            producto.subtotal = producto.precio * producto.cantidad
            productos.append(producto)
            total += producto.subtotal
        except VentaSoftware.DoesNotExist:
            # Maneja el caso donde el producto no existe
            messages.warning(request, f"El producto con ID {id_producto} no existe en la base de datos. Se eliminará del carrito.")
            del carrito[id_producto]  # Eliminar del carrito si no existe
            request.session['carrito'] = carrito  # Actualizar la sesión
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}")

    return render(request, 'API/carrito/carrito.html', {'data': productos, 'total': total})



def eliminar_item_carrito(request, id_producto):
    carrito = request.session.get('carrito', {})

    if str(id_producto) in carrito:
        del carrito[str(id_producto)]
        request.session['carrito'] = carrito
        request.session['items_carrito'] = sum(item['cantidad'] for item in carrito.values())
        messages.success(request, "Producto eliminado del carrito.")
    else:
        messages.error(request, "El producto no está en el carrito.")

    return redirect('ver_carrito')

def vaciar_carrito(request):
    request.session['carrito'] = {}
    request.session['items_carrito'] = 0
    messages.success(request, "Carrito vaciado con éxito.")
    return redirect('tienda')


@transaction.atomic
def guardar_compra(request):
    carrito = request.session.get('carrito', {})

    # Validación: Verificar que el carrito no esté vacío
    if not carrito:
        messages.error(request, "El carrito está vacío. No se puede realizar la compra.")
        return redirect('ver_carrito')

    # Validación: Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para realizar una compra.")
        return redirect('login')

    total_compra = sum(item['subtotal'] for item in carrito.values())

    # Crear la compra
    try:
        compra = Compra.objects.create(usuario=request.user, fecha=timezone.now(), estado=1)

        for producto_id, detalles in carrito.items():
            producto = get_object_or_404(VentaSoftware, id=producto_id)

            # Validación de stock
            if producto.stock < detalles['cantidad']:
                messages.error(request, f"No hay suficiente stock disponible para {producto.nombre}.")
                return redirect('ver_carrito')

            # Guardar detalles de la compra
            Compra.objects.create(compra=compra, producto=producto, cantidad=detalles['cantidad'], precio=producto.precio)

            # Reducir stock
            producto.stock -= detalles['cantidad']
            producto.save()

        # Vaciar el carrito
        request.session['carrito'] = {}
        request.session['items_carrito'] = 0

        messages.success(request, f"Compra realizada con éxito. Total pagado: ${total_compra}")
        return redirect('tienda')

    except Exception as e:
        messages.error(request, f"Hubo un error al procesar la compra: {str(e)}")
        return redirect('ver_carrito')


def productos_listar_software(request):
    logueo = request.session.get("logueo", False)

    if logueo and (logueo["rol"] == "ADMIN"):
        productos = VentaSoftware.objects.all()
        context = {"data": productos}
        return render(request, "API/carrito/listarSoftware/listarSoftware.html", context)
    else:
        messages.info(request, "No tiene permisos para acceder al módulo.")
        return redirect("index")


def productos_guardar_software(request):
    if request.method == "POST":
        foto = request.FILES.get("foto")
        if not foto:
            foto = "fotos_paquetes/default.png"  # Asumiendo que tienes una imagen por defecto.
        
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        stock = request.POST.get("stock", "0").strip()
        precio = request.POST.get("precio", "0").strip()

        # Validaciones manuales
        if not nombre or len(nombre) < 3:
            messages.error(request, "El nombre es obligatorio y debe tener al menos 3 caracteres.")
            return redirect("productos_formulario")
        
        if not descripcion or len(descripcion) < 10:
            messages.error(request, "La descripción es obligatoria y debe tener al menos 10 caracteres.")
            return redirect("productos_formulario")
        
        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError("El stock no puede ser negativo.")
        except ValueError:
            messages.error(request, "El stock debe ser un número entero no negativo.")
            return redirect("productos_formulario")

        try:
            precio = float(precio)
            if precio < 0:
                raise ValueError("El precio no puede ser negativo.")
        except ValueError:
            messages.error(request, "El precio debe ser un número válido y no puede ser negativo.")
            return redirect("productos_formulario")

        try:
            nuevo_producto = VentaSoftware(
                foto=foto, nombre=nombre, stock=stock, descripcion=descripcion, precio=precio
            )
            nuevo_producto.full_clean()  # Validación de modelo
            nuevo_producto.save()
            messages.success(request, "Registro guardado correctamente.")
        except ValidationError as e:
            messages.error(request, f"Error en la validación del producto: {e}")
        except Exception as e:
            messages.error(request, f"Error al guardar el producto: {e}")
        
        return redirect("productos_listar_software")
    else:
        messages.warning(request, "No se enviaron datos.")
        return redirect("productos_formulario")


def productos_actualizar_software(request):
    if request.method == "POST":
        producto = get_object_or_404(VentaSoftware, pk=request.POST.get("id"))

        foto = request.FILES.get("foto")
        if not foto:
            foto = producto.foto  # Mantener la foto actual si no se selecciona una nueva.
        
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        stock = request.POST.get("stock", "0").strip()
        precio = request.POST.get("precio", "0").strip()

        # Validaciones manuales
        if not nombre or len(nombre) < 3:
            messages.error(request, "El nombre es obligatorio y debe tener al menos 3 caracteres.")
            return redirect("productos_formulario")

        if not descripcion or len(descripcion) < 10:
            messages.error(request, "La descripción es obligatoria y debe tener al menos 10 caracteres.")
            return redirect("productos_formulario")

        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError("El stock no puede ser negativo.")
        except ValueError:
            messages.error(request, "El stock debe ser un número entero no negativo.")
            return redirect("productos_formulario")

        try:
            precio = float(precio)
            if precio < 0:
                raise ValueError("El precio no puede ser negativo.")
        except ValueError:
            messages.error(request, "El precio debe ser un número válido y no puede ser negativo.")
            return redirect("productos_formulario")

        try:
            producto.foto = foto
            producto.nombre = nombre
            producto.stock = stock
            producto.descripcion = descripcion
            producto.precio = precio
            producto.full_clean()  # Validación de modelo
            producto.save()
            messages.success(request, "Registro actualizado correctamente.")
        except ValidationError as e:
            messages.error(request, f"Error en la validación del producto: {e}")
        except Exception as e:
            messages.error(request, f"Error al actualizar el producto: {e}")
        
        return redirect("productos_listar_software")


def productos_editar_software(request, id_producto):
    producto = get_object_or_404(VentaSoftware, pk=id_producto)
    contexto = {"registro": producto}
    return render(request, "API/carrito/editarSoftware/editarSoftware.html", contexto)


def productos_eliminar_software(request, id_producto):
    try:
        producto = get_object_or_404(VentaSoftware, pk=id_producto)
        producto.delete()
        messages.success(request, "Registro eliminado correctamente.")
    except Exception as e:
        messages.error(request, f"Error al eliminar el producto: {e}")

    return redirect("productos_listar_software")


def productos_formulario_software(request):
    return render(request, "API/carrito/editarSoftware/editarSoftware.html")


def tienda(request):
    logueo = True  # Esto debería ser gestionado adecuadamente
    if logueo:
        productos = VentaSoftware.objects.all()
        print(productos)  # Agrega esto para depurar
        contexto = {"productos": productos}
        return render(request, 'API/carrito/tienda.html', contexto)
    else:
        return redirect("index")

    
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, 'API/errors/404.html', status=404)

from django.shortcuts import redirect

def custom_404(request, exception):
    messages.error(request, 'La página que estás buscando no existe. Te hemos redirigido al inicio.')
    return redirect('index')


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

# class AlertaStockViewSet(viewsets.ModelViewSet):
#     authentication_classes = [TokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAuthenticated]
#     queryset = AlertaStock.objects.all()
#     serializer_class = AlertaStockSerializer


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


# class MateriaPrimaViewSet(viewsets.ModelViewSet):
#     # authentication_classes = [TokenAuthentication, SessionAuthentication]
#     # permission_classes = [IsAuthenticated]
#     queryset = MateriaPrima.objects.all()
#     serializer_class = MateriaPrimaSerializer


# class MovimientoStockViewSet(viewsets.ModelViewSet):
#     # authentication_classes = [TokenAuthentication, SessionAuthentication]
#     # permission_classes = [IsAuthenticated]
#     queryset = MovimientoStock.objects.all()
#     serializer_class = MovimientoStockSerializer


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


# class RecetaViewSet(viewsets.ModelViewSet):
#     authentication_classes = [TokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAuthenticated]
#     queryset = Receta.objects.all()
#     serializer_class = RecetaSerializer


# class DetallePedidoViewSet(viewsets.ModelViewSet):
#     authentication_classes = [TokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAuthenticated]
#     queryset = DetallePedido.objects.all()
#     serializer_class = DetallePedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer


# class AlertaStockViewSet(viewsets.ModelViewSet):
#     authentication_classes = [TokenAuthentication, SessionAuthentication]
#     permission_classes = [IsAuthenticated]
#     queryset = AlertaStock.objects.all()
#     serializer_class = AlertaStockSerializer


class VentaSoftwareViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = VentaSoftware.objects.all()
    serializer_class = VentaSoftwareSerializer

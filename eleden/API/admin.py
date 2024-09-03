from django.contrib import admin
from .models import *

# Register your models here.
from .models import *

from django.utils.html import mark_safe

admin.site.register(Almacen)
admin.site.register(CategoriaProducto)
admin.site.register(Cliente)
admin.site.register(Devolucion)
admin.site.register(ProductoTerminado)
admin.site.register(Proveedor)
admin.site.register(Pedido)
admin.site.register(Usuario)


class UsuarioAdmin(admin.ModelAdmin):
    list_display = '__all__'

    def ver_foto(self, obj):
        return mark_safe(f"<img src='{obj.foto.url}' width='20%' />")
    
class ventaSoftwareAdmin(admin.ModelAdmin):
    list_display = ["foto","nombre"]

admin.site.register(ventaSoftware,ventaSoftwareAdmin)



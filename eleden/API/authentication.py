from django.contrib.auth.base_user import BaseUserManager

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where `usuario` is used as the unique identifier
    for authentication instead of `username`.
    """
    def create_user(self, usuario, password=None, **extra_fields):
        """
        Create and save a regular User with the given `usuario` and password.
        """
        if not usuario:
            raise ValueError(_('El campo "usuario" debe estar definido'))
        
        user = self.model(usuario=usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, usuario, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given `usuario` and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('El superusuario debe tener is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('El superusuario debe tener is_superuser=True'))

        return self.create_user(usuario, password, **extra_fields)


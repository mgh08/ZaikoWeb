from django.contrib.auth.base_user import BaseUserManager

from rest_framework import authentication
from rest_framework import exceptions

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, usuario, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        print("Creando un usuario....")
        print(password)
        print(extra_fields)
        if not usuario:
            raise ValueError(_('The Email must be set'))
        #email = self.normalize_email(extra_fields["email"])
        user = self.model(usuario=usuario, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, usuario, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        print("Creando un SUPER usuario....")
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(usuario, password, **extra_fields)
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    Add additional fields as needed for your application.
    """
    # Campos existentes del perfil
    email = models.EmailField(unique=True)
    es_modelo = models.BooleanField(default=False)
    telefono_personal = models.CharField(max_length=15, blank=True, null=True)

    # Campos de Verificación
    foto_documento = models.ImageField(upload_to='documentos/', blank=True, null=True)
    selfie_con_documento = models.ImageField(upload_to='selfies/', blank=True, null=True)

    # Campos de Estados
    esta_verificada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.username

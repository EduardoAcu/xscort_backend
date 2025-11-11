from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta


class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    Add additional fields as needed for your application.
    """
    # Campos existentes del perfil
    email = models.EmailField(unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True, help_text="Fecha de nacimiento (debe ser mayor de 18 años)")
    es_modelo = models.BooleanField(default=False)
    telefono_personal = models.CharField(max_length=15, blank=True, null=True)

    # Campos de Verificación
    ha_solicitado_ser_modelo = models.BooleanField(default=False, help_text="Indica si el usuario ha solicitado ser modelo")
    foto_documento = models.ImageField(upload_to='documentos/', blank=True, null=True)
    selfie_con_documento = models.ImageField(upload_to='selfies/', blank=True, null=True)

    # Campos de Estados
    esta_verificada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.username

from django.db import models
from django.conf import settings

from usuarios.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
class PerfilModelo(models.Model):

    # Campos del perfil del modelo
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    nombre_artistico = models.CharField(max_length=100, blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)

    # Contacto Publico
    telefono_contacto = models.CharField(max_length=15, blank=True, null=True)
    telegram_contacto = models.CharField(max_length=50, blank=True, null=True)

    # Ubicación
    ciudad = models.CharField(max_length=100, blank=True, null=True)

    # Características Físicas
    edad = models.PositiveSmallIntegerField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('T', 'Transgénero')], blank=True, null=True)
    peso = models.PositiveSmallIntegerField(blank=True, null=True)
    altura = models.PositiveSmallIntegerField(blank=True, null=True)
    medidas = models.CharField(max_length=50, blank=True, null=True)  # Ejemplo: "90-60-90"
    nacionalidad = models.CharField(max_length=100, blank=True, null=True)

def __str__(self):
        return self.nombre_artistico or self.user.email

@receiver(post_save, sender=CustomUser)
def crear_perfil_modelo(sender, instance, created, **kwargs):
      if created and instance.es_modelo:
            PerfilModelo.objects.create(user=instance)

from django.db import models
from django.conf import settings

from usuarios.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
class PerfilModelo(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='perfil_modelo', null=True, blank=True)

    # Campos del perfil del modelo
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    nombre_artistico = models.CharField(max_length=100, blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)

    # Contacto Publico
    telefono_contacto = models.CharField(max_length=15, blank=True, null=True)
    telegram_contacto = models.CharField(max_length=50, blank=True, null=True)

    # Ubicación
    CIUDADES_CHOICES = [
        ('Rancagua', 'Rancagua'),
        ('Curico', 'Curicó'),
        ('Talca', 'Talca'),
        ('Linares', 'Linares'),
        ('Chillan', 'Chillán'),
        ('Los Angeles', 'Los Ángeles'),
        ('Concepcion', 'Concepción'),
        ('Temuco', 'Temuco'),
        ('Pucon', 'Pucón'),
        ('Valdivia', 'Valdivia'),
        ('Osorno', 'Osorno'),
        ('Puerto Montt', 'Puerto Montt'),
    ]
    ciudad = models.CharField(max_length=100, choices=CIUDADES_CHOICES)

    # Características Físicas
    edad = models.PositiveSmallIntegerField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('T', 'Transgénero')], blank=True, null=True)
    peso = models.PositiveSmallIntegerField(blank=True, null=True)
    altura = models.PositiveSmallIntegerField(blank=True, null=True)
    medidas = models.CharField(max_length=50, blank=True, null=True)  # Ejemplo: "90-60-90"
    nacionalidad = models.CharField(max_length=100, blank=True, null=True)
    
    # Relación Many-to-Many con Tags
    tags = models.ManyToManyField('Tag', related_name='perfiles', blank=True)

    def __str__(self):
        return self.nombre_artistico or (self.user.email if self.user else '')

@receiver(post_save, sender=CustomUser)
def crear_perfil_modelo(sender, instance, created, **kwargs):
    if created and instance.es_modelo:
        PerfilModelo.objects.create(user=instance)

class Servicio(models.Model):
    perfil_modelo = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class GaleriaFoto(models.Model):
    perfil_modelo = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE, related_name='galeria_fotos')
    imagen = models.ImageField(upload_to='galeria_fotos/')

    def __str__(self):
        return f"Foto de {self.perfil_modelo.nombre_artistico}"

class Tag(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)  # Ej: "Nacionalidad", "Servicio"

    def __str__(self):
        return f"{self.categoria}: {self.nombre}"

class SolicitudCambioCiudad(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    
    perfil = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE, related_name='solicitudes_cambio_ciudad')
    ciudad_nueva = models.CharField(max_length=100, choices=PerfilModelo.CIUDADES_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Solicitud de Cambio de Ciudad'
        verbose_name_plural = 'Solicitudes de Cambio de Ciudad'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Solicitud de {self.perfil.nombre_artistico or self.perfil.user.email} - {self.ciudad_nueva} ({self.estado})"

from django.db import models
from django.conf import settings

from usuarios.models import CustomUser, validate_image_file
from django.db.models.signals import post_save
from django.dispatch import receiver


class Ciudad(models.Model):
    """Catálogo de ciudades ordenables y activables."""

    nombre = models.CharField(max_length=120, unique=True)
    ordering = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordering", "nombre"]
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"

    def __str__(self):
        return self.nombre


class PerfilModelo(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='perfil_modelo', null=True, blank=True)

    # Campos del perfil del modelo
    foto_perfil = models.ImageField(
        upload_to='fotos_perfil/',
        blank=True,
        null=True,
        validators=[validate_image_file],
    )
    nombre_artistico = models.CharField(max_length=100, blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)

    # Contacto Publico
    telefono_contacto = models.CharField(max_length=15, blank=True, null=True)
    telegram_contacto = models.CharField(max_length=50, blank=True, null=True)

    # Ubicación (catálogo)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, related_name='perfiles')

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

class PerfilLike(models.Model):
    """Marca de 'me gusta' de un cliente sobre un perfil de modelo"""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    perfil_modelo = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'perfil_modelo')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ♥ {self.perfil_modelo.nombre_artistico or self.perfil_modelo.id}"


@receiver(post_save, sender=CustomUser)
def crear_perfil_modelo(sender, instance, created, **kwargs):
    """Asegura que los usuarios marcados como modelo tengan un PerfilModelo.

    - Al crear un usuario con es_modelo=True, se crea el perfil.
    - Si posteriormente en el admin se cambia es_modelo de False a True,
      también se crea el perfil si no existe.
    """
    # Con ciudad como FK obligatoria, evitamos crear automáticamente sin datos.
    # El perfil debe crearse explícitamente cuando se tenga la ciudad.
    return


class ServicioCatalogo(models.Model):
    """Catálogo global de servicios."""

    nombre = models.CharField(max_length=120, unique=True)
    activo = models.BooleanField(default=True)
    permite_custom = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Servicio de catálogo"
        verbose_name_plural = "Servicios de catálogo"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    perfil_modelo = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE, related_name='servicios')
    catalogo = models.ForeignKey(ServicioCatalogo, on_delete=models.PROTECT, related_name='servicios', null=True, blank=True)
    custom_text = models.CharField(max_length=120, blank=True, null=True)

    def clean(self):
        # Si no hay catálogo, debe haber custom_text; si hay catálogo y no permite custom, custom_text debe ir vacío
        if not self.catalogo and not self.custom_text:
            raise models.ValidationError("Debes seleccionar un servicio del catálogo o ingresar un texto personalizado.")
        if self.catalogo and not self.catalogo.permite_custom and self.custom_text:
            raise models.ValidationError("Este servicio del catálogo no permite texto personalizado.")

    def __str__(self):
        base = self.catalogo.nombre if self.catalogo else (self.custom_text or "")
        if self.custom_text and self.catalogo:
            return f"{base} ({self.custom_text})"
        return base


class GaleriaFoto(models.Model):
    perfil_modelo = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE, related_name='galeria_fotos')
    imagen = models.ImageField(
        upload_to='galeria_fotos/',
        validators=[validate_image_file],
    )

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
    ciudad_nueva = models.ForeignKey(Ciudad, on_delete=models.PROTECT, related_name='solicitudes_cambio_ciudad')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Solicitud de Cambio de Ciudad'
        verbose_name_plural = 'Solicitudes de Cambio de Ciudad'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Solicitud de {self.perfil.nombre_artistico or self.perfil.user.email} - {self.ciudad_nueva} ({self.estado})"

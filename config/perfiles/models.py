from django.db import models
from django.conf import settings


class PerfilModelo(models.Model):
    """
    Perfil extendido para modelos/escorts.
    Relación 1-a-1 con CustomUser.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_modelo',
        primary_key=True
    )
    
    # Información básica
    nombre_publico = models.CharField(
        max_length=150,
        blank=True,
        help_text='Nombre artístico o público'
    )
    biografia = models.TextField(
        blank=True,
        help_text='Biografía o descripción personal'
    )
    telefono_trabajo = models.CharField(
        max_length=15,
        blank=True,
        help_text='Teléfono de contacto profesional'
    )
    telegram_usuario = models.CharField(
        max_length=100,
        blank=True,
        help_text='Usuario de Telegram'
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        editable=False,
        help_text='Ciudad (no editable directamente por la modelo)'
    )
    
    # Información física
    peso_kg = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text='Peso en kilogramos'
    )
    estatura_cm = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text='Estatura en centímetros'
    )
    medidas = models.CharField(
        max_length=50,
        blank=True,
        help_text='Medidas corporales (ej: 90-60-90)'
    )
    
    # Foto de portada
    foto_portada = models.ImageField(
        upload_to='perfiles/portadas/',
        blank=True,
        null=True,
        help_text='Foto de portada del perfil'
    )
    
    # Información profesional
    tarifa_por_hora = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Tarifa por hora en la moneda local'
    )
    servicios_ofrecidos = models.TextField(
        blank=True,
        help_text='Descripción de servicios ofrecidos'
    )
    disponibilidad = models.CharField(
        max_length=200,
        blank=True,
        help_text='Horarios de disponibilidad'
    )
    acepta_visitas_domicilio = models.BooleanField(default=False)
    acepta_encuentros_hotel = models.BooleanField(default=False)
    
    # Configuración de perfil
    perfil_activo = models.BooleanField(
        default=True,
        help_text='Perfil visible en búsquedas'
    )
    perfil_destacado = models.BooleanField(
        default=False,
        help_text='Perfil destacado en la plataforma'
    )
    
    # Estadísticas
    visualizaciones = models.PositiveIntegerField(
        default=0,
        help_text='Número de veces que el perfil ha sido visto'
    )
    
    # Relaciones
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='perfiles',
        help_text='Tags asociados al perfil'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Modelo'
        verbose_name_plural = 'Perfiles de Modelos'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"


class Servicio(models.Model):
    """
    Servicios ofrecidos por una modelo.
    Relación ForeignKey con PerfilModelo.
    """
    perfil = models.ForeignKey(
        PerfilModelo,
        on_delete=models.CASCADE,
        related_name='servicios',
        help_text='Perfil al que pertenece este servicio'
    )
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre del servicio'
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio del servicio'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class GaleriaFoto(models.Model):
    """
    Galería de fotos de una modelo.
    Relación ForeignKey con PerfilModelo.
    """
    perfil = models.ForeignKey(
        PerfilModelo,
        on_delete=models.CASCADE,
        related_name='galeria_fotos',
        help_text='Perfil al que pertenece esta foto'
    )
    imagen = models.ImageField(
        upload_to='perfiles/galeria/',
        help_text='Foto de la galería'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Foto de Galería'
        verbose_name_plural = 'Fotos de Galería'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Foto de {self.perfil.user.username} - {self.created_at.strftime('%Y-%m-%d')}"


class Tag(models.Model):
    """
    Etiquetas o tags para categorizar perfiles.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nombre del tag'
    )
    categoria = models.CharField(
        max_length=100,
        blank=True,
        help_text='Categoría del tag'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        if self.categoria:
            return f"{self.categoria}: {self.nombre}"
        return self.nombre

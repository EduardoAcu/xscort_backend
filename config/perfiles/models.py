from django.db import models
from django.conf import settings
from django.utils.text import slugify
from usuarios.models import CustomUser, validate_image_file
import uuid
# Asegúrate de que utils.py esté en la misma carpeta, o ajusta el import
from .utils import comprimir_imagen 

# --- Utilidades para rutas de archivos ---
def ruta_foto_perfil(instance, filename):
    # Genera: perfiles/user_15/avatar_a1b2c3d4.webp (Forzamos extensión si quieres, pero utils ya lo hace)
    ext = filename.split('.')[-1]
    filename = f"avatar_{uuid.uuid4().hex[:8]}.{ext}"
    return f"perfiles/user_{instance.user.id}/{filename}"

def ruta_galeria(instance, filename):
    # Genera: perfiles/user_15/galeria/foto_a1b2c3d4.webp
    ext = filename.split('.')[-1]
    filename = f"foto_{uuid.uuid4().hex[:8]}.{ext}"
    return f"perfiles/user_{instance.perfil_modelo.user.id}/galeria/{filename}"


# --- Modelos de Catálogos (Simples) ---

class Ciudad(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    activa = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "nombre"]
        verbose_name_plural = "Ciudades"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    """Ej: Oral, Anal, Masajes, Parejas"""
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icono = models.CharField(max_length=50, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Tag(models.Model):
    """Ej: Rubia, Tatuada, Universitarias"""
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    categoria = models.CharField(max_length=50, default="General") 

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# --- Modelo Principal ---

class PerfilModelo(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='perfil_modelo')
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    # Información Básica
    nombre_artistico = models.CharField(max_length=100)
    biografia = models.TextField(blank=True, null=True)
    
    # Imágenes (Se comprimirán al guardar)
    foto_perfil = models.ImageField(upload_to=ruta_foto_perfil, validators=[validate_image_file], blank=True, null=True)
    foto_portada = models.ImageField(upload_to=ruta_foto_perfil, validators=[validate_image_file], blank=True, null=True)

    # Ubicación y Contacto
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, related_name='perfiles')
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True, help_text="Solo números, con código país")
    telegram_contacto = models.CharField(max_length=50, blank=True, null=True)

    # Características Físicas
    edad = models.PositiveSmallIntegerField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('T', 'Transgénero')], default='F')
    altura = models.PositiveSmallIntegerField(blank=True, null=True, help_text="En cm")
    peso = models.PositiveSmallIntegerField(blank=True, null=True, help_text="En kg")
    medidas = models.CharField(max_length=20, blank=True, null=True, help_text="Ej: 90-60-90")
    # Nota: color_pelo y nacionalidad los manejaremos con Tags preferiblemente, pero los dejaste aquí
    color_pelo = models.CharField(max_length=30, blank=True, null=True)
    nacionalidad = models.CharField(max_length=50, blank=True, null=True)

    # RELACIONES DIRECTAS
    servicios = models.ManyToManyField(Servicio, related_name='perfiles', blank=True)
    tags = models.ManyToManyField(Tag, related_name='perfiles', blank=True)

    # Estados
    esta_publico = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 1. Generación de Slug
        if not self.slug and self.nombre_artistico:
            base = f"{self.nombre_artistico}-{self.ciudad.nombre}"
            self.slug = slugify(base)
            if PerfilModelo.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:4]}"

        # 2. Compresión de Imágenes (WebP)
        # Verificamos si es una actualización para no recomprimir lo que no cambió
        if self.pk:
            try:
                old_instance = PerfilModelo.objects.get(pk=self.pk)
                
                # Foto Perfil (Max 800px ancho es suficiente)
                if self.foto_perfil and self.foto_perfil != old_instance.foto_perfil:
                    self.foto_perfil = comprimir_imagen(self.foto_perfil, max_width=800)
                
                # Foto Portada (Max 1200px o 1600px ancho)
                if self.foto_portada and self.foto_portada != old_instance.foto_portada:
                    self.foto_portada = comprimir_imagen(self.foto_portada, max_width=1200)
            except PerfilModelo.DoesNotExist:
                pass # Caso raro, se comporta como creación
        else:
            # Creación nueva
            if self.foto_perfil:
                self.foto_perfil = comprimir_imagen(self.foto_perfil, max_width=800)
            if self.foto_portada:
                self.foto_portada = comprimir_imagen(self.foto_portada, max_width=1200)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_artistico


class GaleriaFoto(models.Model):
    perfil_modelo = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE, related_name='galeria_fotos')
    imagen = models.ImageField(upload_to=ruta_galeria, validators=[validate_image_file])
    orden = models.PositiveIntegerField(default=0)
    es_publica = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden', '-id']

    def save(self, *args, **kwargs):
        # Compresión de imágenes de galería
        if self.pk:
            try:
                old_instance = GaleriaFoto.objects.get(pk=self.pk)
                if self.imagen and self.imagen != old_instance.imagen:
                    self.imagen = comprimir_imagen(self.imagen, max_width=1200)
            except GaleriaFoto.DoesNotExist:
                pass
        else:
            if self.imagen:
                self.imagen = comprimir_imagen(self.imagen, max_width=1200)
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Foto {self.id} - {self.perfil_modelo}"
class PerfilLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    perfil_modelo = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'perfil_modelo')

    def __str__(self):
        return f"Like {self.user} -> {self.perfil_modelo}"
    
class SolicitudCambioCiudad(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    
    perfil = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE, related_name='solicitudes_cambio_ciudad')
    ciudad_nueva = models.ForeignKey(Ciudad, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Auditoría
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    nota_admin = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name = "Solicitud de Cambio de Ciudad"
        verbose_name_plural = "Solicitudes de Cambio de Ciudad"
    
    def __str__(self):
        return f"Cambio a {self.ciudad_nueva} ({self.estado})"
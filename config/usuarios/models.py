from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from datetime import date
from django.core.exceptions import ValidationError


def validate_image_file(image, max_mb=5):
    """Valida tamaño y tipo básico de imagen (JPG/PNG/WEBP, tamaño máximo configurable)."""
    if not image:
        return
    max_bytes = max_mb * 1024 * 1024
    if hasattr(image, 'size') and image.size > max_bytes:
        raise ValidationError(f"El archivo no puede superar los {max_mb}MB.")
    content_type = getattr(image, 'content_type', None)
    valid_types = {'image/jpeg', 'image/png', 'image/webp'}
    if content_type and content_type not in valid_types:
        raise ValidationError("Formato de imagen no soportado. Usa JPG, PNG o WEBP.")


def validate_documento(image):
    """Valida documento de identidad (10MB máx)"""
    return validate_image_file(image, max_mb=10)


def validate_selfie(image):
    """Valida selfie con documento (10MB máx)"""
    return validate_image_file(image, max_mb=10)


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
    terms_version = models.CharField(max_length=50, blank=True, null=True)
    privacy_version = models.CharField(max_length=50, blank=True, null=True)

    # Campos de Verificación
    ha_solicitado_ser_modelo = models.BooleanField(default=False, help_text="Indica si el usuario ha solicitado ser modelo")
    foto_documento = models.ImageField(
        upload_to='documentos/',
        blank=True,
        null=True,
        validators=[validate_documento],
    )
    selfie_con_documento = models.ImageField(
        upload_to='selfies/',
        blank=True,
        null=True,
        validators=[validate_selfie],
    )

    # Campos de Estados
    esta_verificada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        # Garantizar unicidad de username y email
        constraints = [
            models.UniqueConstraint(fields=['username'], name='unique_username'),
            models.UniqueConstraint(fields=['email'], name='unique_email'),
        ]
    
    def __str__(self):
        return self.username


class LegalDocument(models.Model):
    TYPE_CHOICES = [
        ('terms', 'Términos y Condiciones'),
        ('privacy', 'Política de Privacidad'),
    ]
    tipo = models.CharField(max_length=20, choices=TYPE_CHOICES)
    version = models.CharField(max_length=50)
    body = models.TextField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tipo', 'version')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Solo un documento actual por tipo
        if self.is_current:
            LegalDocument.objects.filter(tipo=self.tipo, is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} v{self.version}"


class AgeConsentLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='age_consents')
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    terms_version = models.CharField(max_length=50, blank=True, null=True)
    privacy_version = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-accepted_at']

    def __str__(self):
        return f"Consentimiento {self.user} @ {self.accepted_at}"


# Importar modelo de password reset
from .models_password_reset import PasswordResetToken

from django.contrib.auth.models import AbstractUser
from django.db import models


GENDER_CHOICES = (
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('T', 'Transgénero'),
)

VERIFICATION_STATUS_CHOICES = (
    ('pending', 'Pendiente'),
    ('in_review', 'En Revisión'),
    ('approved', 'Aprobado'),
    ('rejected', 'Rechazado'),
)


class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    Add additional fields as needed for your application.
    """
    # Campos existentes del perfil
    esta_verificada = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    nombre_fantasia = models.CharField(max_length=150, blank=True, null=True)
    genero = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    edad = models.PositiveSmallIntegerField(blank=True, null=True)
    medidas = models.CharField(max_length=100, blank=True, null=True)
    peso = models.PositiveSmallIntegerField(blank=True, null=True)
    altura = models.PositiveSmallIntegerField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)
    
    # Campos de verificación de identidad
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    identity_verified = models.BooleanField(default=False)
    
    # Estado del proceso de verificación
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending'
    )
    
    # Documentos de identidad
    id_document_front = models.ImageField(
        upload_to='documents/id/',
        blank=True,
        null=True,
        help_text='Foto frontal del documento de identidad'
    )
    id_document_back = models.ImageField(
        upload_to='documents/id/',
        blank=True,
        null=True,
        help_text='Foto trasera del documento de identidad'
    )
    selfie = models.ImageField(
        upload_to='documents/selfies/',
        blank=True,
        null=True,
        help_text='Foto Cuerpo Completo para verificación de identidad'
    )
    
    # Información extraída del documento
    document_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Tipo de documento (DNI, Pasaporte, etc.)'
    )
    document_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='Número del documento de identidad'
    )
    
    # Metadatos de verificación
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha y hora de aprobación de la verificación'
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text='Razón del rechazo si la verificación fue rechazada'
    )
    

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.username

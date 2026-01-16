from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets


class PasswordResetTokenManager(models.Manager):
    """Manager personalizado para PasswordResetToken"""
    
    def create_token(self, user):
        """Crea un token con valores por defecto"""
        token_str = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)
        return self.create(
            user=user,
            token=token_str,
            expires_at=expires_at
        )


class PasswordResetToken(models.Model):
    """
    Modelo para gestionar tokens de recuperación de contraseña.
    
    Los tokens expiran después de 1 hora y son de un solo uso.
    """
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    objects = PasswordResetTokenManager()
    
    class Meta:
        verbose_name = 'Token de Recuperación de Contraseña'
        verbose_name_plural = 'Tokens de Recuperación de Contraseña'
        ordering = ['-created_at']
    
    def is_valid(self):
        """
        Verifica si el token es válido:
        - No ha expirado
        - No ha sido usado
        """
        return not self.used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Marca el token como usado"""
        self.used = True
        self.save()
    
    def __str__(self):
        return f"Token de {self.user.username} - {'Válido' if self.is_valid() else 'Inválido'}"

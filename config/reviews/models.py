from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from perfiles.models import PerfilModelo
from usuarios.models import CustomUser


class Resena(models.Model):
    """Modelo para las reseñas de clientes sobre modelos"""
    perfil_modelo = models.ForeignKey(
        PerfilModelo,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    cliente = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='resenas_escritas'
    )
    
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-fecha_creacion']
        unique_together = ['perfil_modelo', 'cliente']
    
    def __str__(self):
        return f"Reseña de {self.cliente.username} para {self.perfil_modelo.nombre_artistico} ({self.rating}★)"

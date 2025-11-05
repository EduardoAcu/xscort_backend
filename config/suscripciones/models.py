from django.db import models
from usuarios.models import CustomUser


class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    dias_contratados = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Planes'

    def __str__(self):
        return f"{self.nombre} - {self.dias_contratados} días - ${self.precio}"


class Suscripcion(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='suscripcion')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='suscripciones')
    dias_restantes = models.IntegerField(default=0)
    esta_pausada = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'

    def __str__(self):
        return f"Suscripción de {self.user.username} - {self.dias_restantes} días"

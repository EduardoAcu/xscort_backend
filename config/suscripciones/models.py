from django.db import models
from usuarios.models import CustomUser
from django.core.exceptions import ValidationError


def validate_comprobante_file(file, max_mb=10):
    """Valida tamaño y tipo básico de comprobante (imagen o PDF)."""
    if not file:
        return
    max_bytes = max_mb * 1024 * 1024
    if hasattr(file, 'size') and file.size > max_bytes:
        raise ValidationError(f"El archivo no puede superar los {max_mb}MB.")
    content_type = getattr(file, 'content_type', None)
    valid_types = {
        'image/jpeg', 'image/png', 'image/webp',
        'application/pdf',
    }
    if content_type and content_type not in valid_types:
        raise ValidationError("Formato de archivo no soportado. Usa JPG, PNG, WEBP o PDF.")


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


class SolicitudSuscripcion(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="solicitudes_suscripcion")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="solicitudes")
    comprobante_pago = models.FileField(
        upload_to="comprobantes_suscripcion/",
        validators=[validate_comprobante_file],
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    nota_admin = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitud de Suscripción"
        verbose_name_plural = "Solicitudes de Suscripción"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Solicitud {self.id} - {self.user.username} - {self.plan.nombre} ({self.estado})"

    def aplicar_plan(self):
        """Aplica el plan de esta solicitud sobre la suscripción del usuario.

        - Crea la suscripción si no existe.
        - Actualiza el plan asociado.
        - Suma los días contratados y marca la suscripción como activa (no pausada).
        """
        suscripcion, created = Suscripcion.objects.get_or_create(
            user=self.user,
            defaults={"plan": self.plan, "dias_restantes": 0},
        )
        suscripcion.plan = self.plan
        suscripcion.dias_restantes += self.plan.dias_contratados
        suscripcion.esta_pausada = False
        suscripcion.save()
        return suscripcion

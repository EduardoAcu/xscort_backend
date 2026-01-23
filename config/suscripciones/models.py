from django.db import models
from usuarios.models import CustomUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import math  # Necesario para el redondeo en la pausa

# --- Validaciones ---

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


# --- Modelos ---

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
    
    # CAMBIO 1: La fecha real de vencimiento. Si es Null, no está corriendo.
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    
    # CAMBIO 2: Este campo ahora es solo un "Congelador" para cuando se pausa.
    dias_restantes = models.IntegerField(default=0, null=True, blank=True)
    
    esta_pausada = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'

    def __str__(self):
        estado = "Pausada" if self.esta_pausada else "Activa"
        return f"Suscripción de {self.user.username} - {estado}"

    # --- Lógica de Negocio Centralizada ---

    def pausar(self):
        """Detiene el reloj y guarda los días restantes en el 'congelador'."""
        if self.esta_pausada or not self.fecha_expiracion:
            return

        now = timezone.now()
        
        # Solo guardamos días si la fecha es futura
        if self.fecha_expiracion > now:
            tiempo_restante = self.fecha_expiracion - now
            # Usamos ceil para redondear hacia arriba (ej: 1.2 días -> 2 días) para no perjudicar al usuario
            dias_a_guardar = math.ceil(tiempo_restante.total_seconds() / (24 * 3600))
            self.dias_restantes = max(dias_a_guardar, 0)
        else:
            self.dias_restantes = 0

        self.fecha_expiracion = None  # Borramos la fecha porque el tiempo se detuvo
        self.esta_pausada = True
        self.save()

    def reanudar(self):
        """Reactiva el reloj sumando los días congelados a HOY."""
        if not self.esta_pausada:
            return

        # Si no tenía días guardados, no hay nada que reanudar, queda expirada
        dias_a_sumar = self.dias_restantes if self.dias_restantes else 0
        
        now = timezone.now()
        self.fecha_expiracion = now + timedelta(days=dias_a_sumar)
        
        self.dias_restantes = 0  # Vaciamos el congelador
        self.esta_pausada = False
        self.save()

    @property
    def es_valida(self):
        """Retorna True si la suscripción está activa y vigente."""
        if self.esta_pausada:
            return False
        if not self.fecha_expiracion:
            return False
        return self.fecha_expiracion > timezone.now()


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
        """
        Aplica el plan solicitado. 
        Maneja correctamente la suma de fechas en lugar de enteros simples.
        """
        now = timezone.now()
        suscripcion, created = Suscripcion.objects.get_or_create(
            user=self.user
        )

        suscripcion.plan = self.plan
        dias_a_agregar = self.plan.dias_contratados

        if suscripcion.esta_pausada:
            # Caso 1: Está pausada -> Sumamos al 'congelador'
            dias_actuales = suscripcion.dias_restantes if suscripcion.dias_restantes else 0
            suscripcion.dias_restantes = dias_actuales + dias_a_agregar
            # Nota: Opcionalmente podrías despausarla aquí automáticamente:
            # suscripcion.reanudar() 
        
        else:
            # Caso 2: Está activa o expirada
            if suscripcion.fecha_expiracion and suscripcion.fecha_expiracion > now:
                # Si está vigente, EXTENDEMOS la fecha actual
                suscripcion.fecha_expiracion += timedelta(days=dias_a_agregar)
            else:
                # Si es nueva o ya expiró, empieza desde HOY
                suscripcion.fecha_expiracion = now + timedelta(days=dias_a_agregar)

        suscripcion.save()
        return suscripcion
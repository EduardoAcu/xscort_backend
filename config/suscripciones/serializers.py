from rest_framework import serializers
from .models import Plan, Suscripcion, SolicitudSuscripcion
from django.utils import timezone
import math  # Importante para el redondeo de días

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'nombre', 'precio', 'dias_contratados']


class SuscripcionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    # Este campo lo calculamos nosotros para facilitar la vida al Frontend
    dias_restantes_calculado = serializers.SerializerMethodField()
    
    class Meta:
        model = Suscripcion
        fields = [
            'id',
            'user',
            'plan',
            'dias_restantes',       # Valor "congelado" (solo útil si está pausada)
            'esta_pausada',
            'fecha_inicio',
            'fecha_actualizacion',
            'fecha_expiracion',     # Ahora se lee directo de la BD (es la fuente de la verdad)
            'dias_restantes_calculado',
        ]
        read_only_fields = ['fecha_inicio', 'fecha_actualizacion', 'fecha_expiracion']

    def get_dias_restantes_calculado(self, obj):
        """
        Devuelve cuántos días de servicio efectivo le quedan al usuario.
        """
        # CASO 1: Suscripción Pausada
        # Devolvemos lo que quedó guardado en el "congelador" (dias_restantes)
        if obj.esta_pausada:
            return obj.dias_restantes if obj.dias_restantes is not None else 0

        # CASO 2: Suscripción Activa
        # Calculamos: Fecha Expiración - Ahora Mismo
        if not obj.fecha_expiracion:
            return 0
            
        now = timezone.now()
        
        # Si la fecha ya pasó, quedan 0 días
        if obj.fecha_expiracion <= now:
            return 0
            
        delta = obj.fecha_expiracion - now
        
        # Matemáticas para redondear hacia arriba:
        # Si quedan 0.1 días (2.4 horas), mostramos 1 día.
        # Si usamos .days de python, 23 horas sería 0 días, y eso asusta al usuario.
        return math.ceil(delta.total_seconds() / (24 * 3600))


class SolicitudSuscripcionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = SolicitudSuscripcion
        fields = [
            'id', 'user', 'plan', 'comprobante_pago', 'estado',
            'nota_admin', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['user', 'estado', 'nota_admin', 'fecha_creacion', 'fecha_actualizacion']
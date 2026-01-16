from rest_framework import serializers
from .models import Plan, Suscripcion, SolicitudSuscripcion
from django.utils import timezone
from datetime import timedelta


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'nombre', 'precio', 'dias_contratados']


class SuscripcionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    dias_restantes_calculado = serializers.SerializerMethodField()
    fecha_expiracion = serializers.SerializerMethodField()
    
    class Meta:
        model = Suscripcion
        fields = [
            'id',
            'user',
            'plan',
            'dias_restantes',
            'esta_pausada',
            'fecha_inicio',
            'fecha_actualizacion',
            'dias_restantes_calculado',
            'fecha_expiracion',
        ]

    def get_fecha_expiracion(self, obj):
        """
        Calcula la fecha de expiración estimada usando la última actualización
        y los días restantes actuales.
        """
        if obj.dias_restantes is None:
            return None
        return (obj.fecha_actualizacion + timedelta(days=obj.dias_restantes)).isoformat()

    def get_dias_restantes_calculado(self, obj):
        """
        Calcula dinámicamente los días restantes en base a la fecha de expiración
        (derivada de fecha_actualizacion + dias_restantes) vs ahora.
        Esto evita depender solo del valor almacenado si no se ha decrementado aún.
        """
        if obj.dias_restantes is None:
            return 0
        fecha_exp = obj.fecha_actualizacion + timedelta(days=obj.dias_restantes)
        delta = (fecha_exp - timezone.now()).days
        return max(delta, 0)


class SolicitudSuscripcionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = SolicitudSuscripcion
        fields = [
            'id', 'user', 'plan', 'comprobante_pago', 'estado',
            'nota_admin', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['user', 'estado', 'nota_admin', 'fecha_creacion', 'fecha_actualizacion']

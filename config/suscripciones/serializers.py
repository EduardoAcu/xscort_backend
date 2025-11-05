from rest_framework import serializers
from .models import Plan, Suscripcion


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'nombre', 'precio', 'dias_contratados']


class SuscripcionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    
    class Meta:
        model = Suscripcion
        fields = ['id', 'user', 'plan', 'dias_restantes', 'esta_pausada', 'fecha_inicio', 'fecha_actualizacion']

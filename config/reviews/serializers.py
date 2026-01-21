from rest_framework import serializers
from .models import Resena


class ResenaSerializer(serializers.ModelSerializer):
    cliente_username = serializers.CharField(source='cliente.username', read_only=True)
    perfil_modelo_nombre = serializers.CharField(source='perfil_modelo.nombre_artistico', read_only=True)
    
    class Meta:
        model = Resena
        fields = [
            'id',
            'perfil_modelo',
            'cliente',
            'cliente_username',
            'perfil_modelo_nombre',
            'rating',
            'comentario',
            'fecha_creacion',
            'aprobada'
        ]
        read_only_fields = ['cliente', 'fecha_creacion', 'aprobada']

from rest_framework import serializers
from .models import PerfilModelo, Servicio, GaleriaFoto, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nombre', 'categoria']


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'perfil_modelo', 'nombre', 'precio']


class GaleriaFotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriaFoto
        fields = ['id', 'perfil_modelo', 'imagen']


class PerfilModeloSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    servicios = ServicioSerializer(many=True, read_only=True)
    galeria_fotos = GaleriaFotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = PerfilModelo
        fields = [
            'id',
            'foto_perfil',
            'nombre_artistico',
            'biografia',
            'telefono_contacto',
            'telegram_contacto',
            'ciudad',
            'edad',
            'genero',
            'peso',
            'altura',
            'medidas',
            'nacionalidad',
            'tags',
            'servicios',
            'galeria_fotos',
        ]
        extra_kwargs = {
            'ciudad': {'required': True},
        }

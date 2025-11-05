from rest_framework import serializers
from .models import PerfilModelo, Servicio, GaleriaFoto, Tag, SolicitudCambioCiudad
from reviews.models import Resena


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


class ResenaAprobadaSerializer(serializers.ModelSerializer):
    cliente_username = serializers.CharField(source='cliente.username', read_only=True)
    
    class Meta:
        model = Resena
        fields = ['id', 'cliente_username', 'rating', 'comentario', 'fecha_creacion']


class PerfilModeloSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    servicios = ServicioSerializer(many=True, read_only=True)
    galeria_fotos = GaleriaFotoSerializer(many=True, read_only=True)
    resenas = serializers.SerializerMethodField()
    
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
            'resenas',
        ]
        extra_kwargs = {
            'ciudad': {'required': True},
        }
    
    def get_resenas(self, obj):
        resenas_aprobadas = obj.resenas.filter(aprobada=True)
        return ResenaAprobadaSerializer(resenas_aprobadas, many=True).data


class SolicitudCambioCiudadSerializer(serializers.ModelSerializer):
    perfil_nombre = serializers.CharField(source='perfil.nombre_artistico', read_only=True)
    
    class Meta:
        model = SolicitudCambioCiudad
        fields = ['id', 'perfil', 'perfil_nombre', 'ciudad_nueva', 'estado', 'fecha_solicitud']
        read_only_fields = ['estado', 'fecha_solicitud']

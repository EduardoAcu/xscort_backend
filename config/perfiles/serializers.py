from rest_framework import serializers
from .models import PerfilModelo, Servicio, GaleriaFoto, Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Tag.
    """
    class Meta:
        model = Tag
        fields = [
            'id',
            'nombre',
            'categoria',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServicioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Servicio.
    """
    class Meta:
        model = Servicio
        fields = [
            'id',
            'perfil',
            'nombre',
            'precio',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GaleriaFotoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo GaleriaFoto.
    """
    class Meta:
        model = GaleriaFoto
        fields = [
            'id',
            'perfil',
            'imagen',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PerfilModeloSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo PerfilModelo.
    """
    servicios = ServicioSerializer(many=True, read_only=True)
    galeria_fotos = GaleriaFotoSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    edad = serializers.IntegerField(source='user.edad', read_only=True)
    
    class Meta:
        model = PerfilModelo
        fields = [
            'user',
            'user_username',
            'edad',
            'nombre_publico',
            'biografia',
            'telefono_trabajo',
            'telegram_usuario',
            'ciudad',
            'peso_kg',
            'estatura_cm',
            'medidas',
            'foto_portada',
            'tarifa_por_hora',
            'servicios_ofrecidos',
            'disponibilidad',
            'acepta_visitas_domicilio',
            'acepta_encuentros_hotel',
            'perfil_activo',
            'perfil_destacado',
            'visualizaciones',
            'tags',
            'servicios',
            'galeria_fotos',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'user',
            'ciudad',
            'visualizaciones',
            'created_at',
            'updated_at'
        ]


class PerfilModeloListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar perfiles (sin relaciones anidadas).
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    edad = serializers.IntegerField(source='user.edad', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = PerfilModelo
        fields = [
            'user',
            'user_username',
            'edad',
            'nombre_publico',
            'ciudad',
            'foto_portada',
            'tarifa_por_hora',
            'perfil_activo',
            'perfil_destacado',
            'visualizaciones',
            'tags',
            'created_at'
        ]
        read_only_fields = [
            'user',
            'ciudad',
            'visualizaciones',
            'created_at'
        ]

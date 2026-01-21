from rest_framework import serializers
from django.conf import settings
from .models import PerfilModelo, Servicio, GaleriaFoto, Tag, SolicitudCambioCiudad, Ciudad, ServicioCatalogo
from reviews.models import Resena


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nombre', 'categoria']


class ServicioCatalogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioCatalogo
        fields = ['id', 'nombre', 'activo', 'permite_custom']


class ServicioSerializer(serializers.ModelSerializer):
    catalogo = ServicioCatalogoSerializer(read_only=True)
    catalogo_id = serializers.PrimaryKeyRelatedField(
        source='catalogo',
        queryset=ServicioCatalogo.objects.filter(activo=True),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Servicio
        fields = ['id', 'perfil_modelo', 'catalogo', 'catalogo_id', 'custom_text']

    def validate(self, attrs):
        catalogo = attrs.get('catalogo')
        custom_text = attrs.get('custom_text')
        if not catalogo and not custom_text:
            raise serializers.ValidationError("Debes elegir un servicio del catálogo o ingresar un texto personalizado.")
        if catalogo and custom_text and not catalogo.permite_custom:
            raise serializers.ValidationError("El servicio seleccionado no permite texto personalizado.")
        return attrs


class GaleriaFotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriaFoto
        fields = ['id', 'perfil_modelo', 'imagen']


class ResenaAprobadaSerializer(serializers.ModelSerializer):
    cliente_username = serializers.CharField(source='cliente.username', read_only=True)
    
    class Meta:
        model = Resena
        fields = ['id', 'cliente_username', 'rating', 'comentario', 'fecha_creacion']


class CiudadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudad
        fields = ['id', 'nombre', 'ordering', 'activa']


class PerfilModeloSerializer(serializers.ModelSerializer):
    ciudad = serializers.CharField(source='ciudad.nombre', read_only=True)
    ciudad_id = serializers.PrimaryKeyRelatedField(
        source='ciudad',
        queryset=Ciudad.objects.filter(activa=True),
        write_only=True,
        required=True
    )
    tags = TagSerializer(many=True, read_only=True)
    servicios = ServicioSerializer(many=True, read_only=True)
    galeria_fotos = GaleriaFotoSerializer(many=True, read_only=True)
    resenas = serializers.SerializerMethodField()
    disclaimer = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    liked_by_me = serializers.SerializerMethodField()
    
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
            'ciudad_id',
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
            'disclaimer',
            'likes_count',
            'liked_by_me',
        ]
        extra_kwargs = {
            'ciudad_id': {'required': True},
        }
    
    def get_resenas(self, obj):
        resenas_aprobadas = obj.resenas.filter(aprobada=True)
        return ResenaAprobadaSerializer(resenas_aprobadas, many=True).data

    def get_disclaimer(self, obj):
        return getattr(settings, "LEGAL_DISCLAIMER", "")

    def get_liked_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and not request.user.es_modelo:
            return obj.likes.filter(user=request.user).exists()
        return False


class SolicitudCambioCiudadSerializer(serializers.ModelSerializer):
    perfil_nombre = serializers.CharField(source='perfil.nombre_artistico', read_only=True)
    ciudad_nueva = serializers.CharField(source='ciudad_nueva.nombre', read_only=True)
    ciudad_nueva_id = serializers.PrimaryKeyRelatedField(
        source='ciudad_nueva',
        queryset=Ciudad.objects.filter(activa=True),
        write_only=True,
        required=True,
    )
    
    class Meta:
        model = SolicitudCambioCiudad
        fields = ['id', 'perfil', 'perfil_nombre', 'ciudad_nueva', 'ciudad_nueva_id', 'estado', 'fecha_solicitud']
        read_only_fields = ['estado', 'fecha_solicitud']


class PerfilModeloUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating PerfilModelo. 
    Excludes ciudad field - city changes must go through SolicitudCambioCiudad.
    """
    class Meta:
        model = PerfilModelo
        fields = [
            'foto_perfil',
            'nombre_artistico',
            'biografia',
            'telefono_contacto',
            'telegram_contacto',
            'edad',
            'genero',
            'peso',
            'altura',
            'medidas',
            'nacionalidad',
        ]
        # Ciudad is intentionally excluded - it can only be changed via SolicitudCambioCiudad

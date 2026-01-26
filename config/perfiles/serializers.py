from rest_framework import serializers
from django.conf import settings
from .models import PerfilModelo, Servicio, GaleriaFoto, Tag, SolicitudCambioCiudad, Ciudad, Servicio
from reviews.models import Resena

# --- Serializers de Catálogos (Simples) ---

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nombre', 'slug', 'categoria']

# CORRECCIÓN AQUÍ: Agregamos 'slug'
class ServicioCatalogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        # Antes: fields = ['id', 'nombre']
        fields = ['id', 'nombre', 'slug'] 

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'slug', 'icono', 'activo']

class CiudadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudad
        fields = ['id', 'nombre', 'slug', 'activa', 'ordering']


# --- Serializers de Contenido ---

class GaleriaFotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriaFoto
        fields = ['id', 'imagen', 'orden', 'es_publica']


class ResenaAprobadaSerializer(serializers.ModelSerializer):
    cliente_username = serializers.CharField(source='cliente.username', read_only=True)
    
    class Meta:
        model = Resena
        fields = ['id', 'cliente_username', 'rating', 'comentario', 'fecha_creacion']


# --- Serializer PRINCIPAL de Perfil (Lectura Pública - GET) ---

class PerfilModeloSerializer(serializers.ModelSerializer):
    # Relaciones expandidas para lectura fácil (Objetos completos)
    ciudad = CiudadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    servicios = ServicioSerializer(many=True, read_only=True)
    
    galeria_fotos = serializers.SerializerMethodField()
    
    # Campos calculados
    resenas = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    liked_by_me = serializers.SerializerMethodField()
    
    class Meta:
        model = PerfilModelo
        fields = [
            'id',
            'slug',
            'user',
            'foto_perfil',
            'foto_portada',
            'nombre_artistico',
            'biografia',
            'telefono_contacto',
            'whatsapp',
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
            'likes_count',
            'liked_by_me',
            'esta_publico',
        ]
        read_only_fields = ['slug', 'user', 'likes_count', 'liked_by_me']
    
    def get_galeria_fotos(self, obj):
        fotos = obj.galeria_fotos.filter(es_publica=True).order_by('orden')
        return GaleriaFotoSerializer(fotos, many=True).data

    def get_resenas(self, obj):
        if hasattr(obj, 'resenas'):
            resenas_aprobadas = obj.resenas.filter(aprobada=True)
            return ResenaAprobadaSerializer(resenas_aprobadas, many=True).data
        return []

    def get_liked_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


# --- Serializer de EDICIÓN (Para el Panel - PATCH/PUT) ---

class PerfilModeloUpdateSerializer(serializers.ModelSerializer):
    """
    Se usa cuando la modelo edita su propio perfil.
    Diferencia: 'servicios' y 'tags' aceptan LISTAS DE IDs.
    """
    
    # ESTA ES LA MAGIA: Acepta [1, 2, 3] y guarda las relaciones
    servicios = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Servicio.objects.filter(activo=True),
        required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Tag.objects.all(),
        required=False
    )
    
    # La ciudad es read_only aquí porque se cambia vía solicitud
    ciudad_nombre = serializers.CharField(source='ciudad.nombre', read_only=True)

    class Meta:
        model = PerfilModelo
        fields = [
            'foto_perfil',
            'foto_portada',
            'nombre_artistico',
            'biografia',
            'telefono_contacto',
            'whatsapp',
            'telegram_contacto',
            'edad',
            'genero',        
            'altura',
            'peso',
            'medidas',       
            'nacionalidad',  
            'ciudad_nombre',
            'servicios',     
            'tags',          
            'esta_publico',
        ]

    def to_representation(self, instance):
        """
        Cuando respondes al Frontend después de guardar, 
        devuelves IDs en lugar de objetos para facilitar la UI.
        """
        rep = super().to_representation(instance)
        rep['servicios'] = [s.id for s in instance.servicios.all()]
        rep['tags'] = [t.id for t in instance.tags.all()]
        return rep


# --- Serializer de Cambio de Ciudad ---

class SolicitudCambioCiudadSerializer(serializers.ModelSerializer):
    ciudad_nueva_nombre = serializers.CharField(source='ciudad_nueva.nombre', read_only=True)
    
    # IMPORTANTE: El frontend debe enviar 'ciudad_nueva' (el ID)
    ciudad_nueva = serializers.PrimaryKeyRelatedField(
        queryset=Ciudad.objects.filter(activa=True),
        write_only=True,
        required=True,
    )
    
    class Meta:
        model = SolicitudCambioCiudad
        fields = ['id', 'estado', 'fecha_solicitud', 'ciudad_nueva', 'ciudad_nueva_nombre', 'nota_admin']
        read_only_fields = ['estado', 'fecha_solicitud', 'nota_admin']
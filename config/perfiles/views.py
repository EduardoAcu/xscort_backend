from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import uuid
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend

# --- CORRECCIÓN 1: Importar correctamente el filtro ---
from .filters import PerfilFilter

from .models import (
    PerfilModelo, 
    SolicitudCambioCiudad, 
    Servicio, 
    GaleriaFoto, 
    Tag, 
    Ciudad, 
    PerfilLike,
)
from .serializers import (
    PerfilModeloSerializer,
    PerfilModeloUpdateSerializer,
    SolicitudCambioCiudadSerializer,
    ServicioSerializer,
    TagSerializer,
    CiudadSerializer,
    GaleriaFotoSerializer,
    ServicioCatalogoSerializer
)

# --- CONFIGURACIÓN DE PAGINACIÓN ---
class PerfilesPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


# --- 1. VISTAS PÚBLICAS (Catálogos) ---
class CiudadListView(generics.ListAPIView):
    queryset = Ciudad.objects.filter(activa=True).order_by('ordering', 'nombre')
    serializer_class = CiudadSerializer
    permission_classes = [permissions.AllowAny]
    
    # AGREGAR ESTO: Desactiva paginación para que devuelva una lista simple [{},{}]
    pagination_class = None 

    @method_decorator(cache_page(300))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class ServicioListView(generics.ListAPIView):
    """Catálogo de servicios (Oral, Anal...)"""
    queryset = Servicio.objects.filter(activo=True).order_by('nombre')
    serializer_class = ServicioSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(300))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class TagListView(generics.ListAPIView):
    """Catálogo de Tags (Rubia, Alta...)"""
    queryset = Tag.objects.all().order_by('categoria', 'nombre')
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


# --- 2. VISTAS PÚBLICAS (Perfiles) ---

class PerfilModeloListView(generics.ListAPIView):
    """
    Buscador principal. 
    Usa PerfilFilter para manejar ?ciudad=santiago&servicio=masajes
    """
    serializer_class = PerfilModeloSerializer
    pagination_class = PerfilesPagination
    permission_classes = [permissions.AllowAny]

    # --- CORRECCIÓN 2: Configurar Backends de Filtrado ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Conectamos tu clase de filtros personalizada
    filterset_class = PerfilFilter
    
    # Configuración de Búsqueda de Texto (?search=...)
    search_fields = ['nombre_artistico', 'biografia', 'ciudad__nombre', 'tags__nombre']
    
    # Configuración de Ordenamiento (?ordering=...)
    ordering_fields = ['id', 'created_at', 'puntuacion'] # Ajusta según tus campos

    def get_queryset(self):
        # 1. Filtros Base de Negocio (Solo lo que DEBE verse)
        queryset = PerfilModelo.objects.filter(
            esta_publico=True,
            # user__esta_verificada=True, # Descomentar cuando actives
            # user__suscripcion__dias_restantes__gt=0,
            # user__suscripcion__esta_pausada=False,
        )
        
        # Optimización de DB
        queryset = queryset.select_related('ciudad', 'user').prefetch_related('tags', 'servicios', 'galeria_fotos')
        
        # NOTA: Ya no necesitamos filtrar manualmente aquí (if ciudad...). 
        # DjangoFilterBackend lo hace automáticamente usando filterset_class.
        
        return queryset.order_by('-id')


class PerfilModeloDetailView(generics.RetrieveAPIView):
    """Ver perfil individual por SLUG"""
    serializer_class = PerfilModeloSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return PerfilModelo.objects.filter(
            esta_publico=True,
            # user__esta_verificada=True,
        )


# --- 3. VISTAS PRIVADAS (Gestión de la Modelo) ---

class MiPerfilView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return PerfilModeloUpdateSerializer
        return PerfilModeloSerializer

    def get_object(self):
        perfil, created = PerfilModelo.objects.get_or_create(user=self.request.user)
        
        # Auto-reparación de slug
        if not perfil.slug:
            base_slug = slugify(self.request.user.username) or "usuario"
            perfil.slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
            perfil.save()

        return perfil


class MiGaleriaView(generics.ListCreateAPIView):
    serializer_class = GaleriaFotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GaleriaFoto.objects.filter(perfil_modelo__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(perfil_modelo=self.request.user.perfil_modelo)


class GaleriaDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = GaleriaFotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GaleriaFoto.objects.filter(perfil_modelo__user=self.request.user)


class SolicitudCambioCiudadCreateView(generics.CreateAPIView):
    queryset = SolicitudCambioCiudad.objects.all()
    serializer_class = SolicitudCambioCiudadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        perfil = self.request.user.perfil_modelo
        if SolicitudCambioCiudad.objects.filter(perfil=perfil, estado='pendiente').exists():
            raise filters.ValidationError("Ya tienes una solicitud pendiente.")
        serializer.save(perfil=perfil)


# --- 4. ACCIONES (Likes) ---

class ToggleLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, perfil_id):
        perfil = get_object_or_404(PerfilModelo, id=perfil_id)
        like, created = PerfilLike.objects.get_or_create(user=request.user, perfil_modelo=perfil)
        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

class MisLikesView(generics.ListAPIView):
    serializer_class = PerfilModeloSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PerfilModelo.objects.filter(likes__user=self.request.user, esta_publico=True)

# --- 5. VISTA DE CATÁLOGO (Para Dropdowns) ---
    
class ServicioCatalogoView(generics.ListAPIView):
    """
    Devuelve la lista completa de servicios para usar en filtros.
    """
    queryset = Servicio.objects.all().order_by('nombre')
    serializer_class = ServicioCatalogoSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import PerfilModelo, SolicitudCambioCiudad
from .serializers import PerfilModeloSerializer, SolicitudCambioCiudadSerializer


class PerfilesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_perfiles(request):
    """
    Endpoint público para listar todos los perfiles de modelos.
    Solo muestra perfiles con:
    - esta_verificada=True
    - suscripcion.dias_restantes > 0
    - suscripcion.esta_pausada=False
    
    Filtros disponibles:
    - ciudad: ?ciudad=Concepcion
    - tags: ?tags=tag1,tag2 (filtra por cualquiera de los tags)
    - search: ?search=texto (busca en nombre_artistico y biografia)
    
    Paginación: 10 perfiles por página (configurable con ?page_size=N)
    """
    perfiles = PerfilModelo.objects.filter(
        user__esta_verificada=True,
        user__suscripcion__dias_restantes__gt=0,
        user__suscripcion__esta_pausada=False
    )
    
    # Filtro por ciudad
    ciudad = request.query_params.get('ciudad', None)
    if ciudad:
        perfiles = perfiles.filter(ciudad=ciudad)
    
    # Filtro por tags (separados por coma)
    tags = request.query_params.get('tags', None)
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
        perfiles = perfiles.filter(tags__nombre__in=tag_list).distinct()
    
    # Búsqueda por texto en nombre_artistico y biografia
    search = request.query_params.get('search', None)
    if search:
        perfiles = perfiles.filter(
            Q(nombre_artistico__icontains=search) |
            Q(biografia__icontains=search)
        )
    
    paginator = PerfilesPagination()
    paginated_perfiles = paginator.paginate_queryset(perfiles, request)
    serializer = PerfilModeloSerializer(paginated_perfiles, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def ver_perfil(request, id):
    """
    Endpoint público para ver un perfil de modelo por ID.
    Solo muestra perfiles con:
    - esta_verificada=True
    - suscripcion.dias_restantes > 0
    - suscripcion.esta_pausada=False
    """
    try:
        perfil = PerfilModelo.objects.get(
            id=id,
            user__esta_verificada=True,
            user__suscripcion__dias_restantes__gt=0,
            user__suscripcion__esta_pausada=False
        )
        serializer = PerfilModeloSerializer(perfil)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except PerfilModelo.DoesNotExist:
        return Response({"error": "Perfil no encontrado o no disponible"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_perfil(request):
    """
    Crear perfil de modelo. El campo ciudad es requerido.
    """
    serializer = PerfilModeloSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def solicitar_cambio_ciudad(request):
    """
    Endpoint para que una modelo cree una solicitud de cambio de ciudad.
    Requiere autenticación y que el usuario tenga un perfil de modelo.
    
    Body esperado:
    {
        "ciudad_nueva": "Concepcion"
    }
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verificar si ya existe una solicitud pendiente
    solicitud_pendiente = SolicitudCambioCiudad.objects.filter(
        perfil=perfil,
        estado='pendiente'
    ).exists()
    
    if solicitud_pendiente:
        return Response(
            {"error": "Ya tienes una solicitud de cambio de ciudad pendiente"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Crear la solicitud
    data = request.data.copy()
    data['perfil'] = perfil.id
    
    serializer = SolicitudCambioCiudadSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

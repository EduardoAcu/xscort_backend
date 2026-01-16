from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import cache_page
from .models import PerfilModelo, SolicitudCambioCiudad, Servicio, GaleriaFoto, Tag, Ciudad, PerfilLike, ServicioCatalogo
from .serializers import PerfilModeloSerializer, SolicitudCambioCiudadSerializer, PerfilModeloUpdateSerializer, ServicioSerializer, GaleriaFotoSerializer, TagSerializer, CiudadSerializer, ServicioCatalogoSerializer
from .permissions import IsProfileOwner, IsModeloUser

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_ciudades(request):
    """
    Devuelve las ciudades permitidas según choices de PerfilModelo.
    """
    ciudades = Ciudad.objects.filter(activa=True).order_by('ordering', 'nombre')
    serializer = CiudadSerializer(ciudades, many=True)
    # Front espera value/label; mantenemos compatibilidad
    data = [{"value": c['id'], "label": c['nombre']} for c in serializer.data]
    return Response(data, status=status.HTTP_200_OK)


class PerfilesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60)  # cachea 60 segundos las listas públicas de perfiles
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
    perfiles_qs = (
        PerfilModelo.objects.filter(
            user__esta_verificada=True,
            user__suscripcion__dias_restantes__gt=0,
            user__suscripcion__esta_pausada=False,
        )
        .select_related('user', 'user__suscripcion')
        .prefetch_related(
            'tags',
            'servicios',
            'galeria_fotos',
            'resenas',
            'resenas__cliente',
        )
    )
    
    # Filtro por ciudad (acepta id o nombre para compatibilidad)
    ciudad = request.query_params.get('ciudad', None)
    if ciudad:
        if ciudad.isdigit():
            perfiles_qs = perfiles_qs.filter(ciudad__id=int(ciudad))
        else:
            perfiles_qs = perfiles_qs.filter(ciudad__nombre__iexact=ciudad)
    
    # Filtro por tags (separados por coma)
    tags = request.query_params.get('tags', None)
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
        perfiles_qs = perfiles_qs.filter(tags__nombre__in=tag_list).distinct()
    # Filtro por servicio (nombre contiene)
    servicio = request.query_params.get('servicio', None)
    if servicio:
        perfiles_qs = perfiles_qs.filter(servicios__nombre__icontains=servicio).distinct()
    
    # Búsqueda por texto en nombre_artistico y biografia
    search = request.query_params.get('search', None)
    if search:
        perfiles_qs = perfiles_qs.filter(
            Q(nombre_artistico__icontains=search) |
            Q(biografia__icontains=search)
        )
    
    paginator = PerfilesPagination()
    paginated_perfiles = paginator.paginate_queryset(perfiles_qs, request)
    serializer = PerfilModeloSerializer(paginated_perfiles, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60)  # cachea 60 segundos la vista pública de un perfil
def ver_perfil(request, id):
    """
    Endpoint público para ver un perfil de modelo por ID.
    Solo muestra perfiles con:
    - esta_verificada=True
    - suscripcion.dias_restantes > 0
    - suscripcion.esta_pausada=False
    """
    try:
        perfil = (
            PerfilModelo.objects.select_related('user', 'user__suscripcion')
            .prefetch_related(
                'tags',
                'servicios',
                'galeria_fotos',
                'resenas',
                'resenas__cliente',
            )
            .get(
                id=id,
                user__esta_verificada=True,
                user__suscripcion__dias_restantes__gt=0,
                user__suscripcion__esta_pausada=False,
            )
        )
        serializer = PerfilModeloSerializer(perfil, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except PerfilModelo.DoesNotExist:
        return Response({"error": "Perfil no encontrado o no disponible"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsModeloUser])
def mi_perfil(request):
    """Devuelve el perfil de modelo asociado al usuario autenticado."""
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = PerfilModeloSerializer(perfil, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(300)
def listar_servicios_catalogo(request):
    """
    Lista el catálogo global de servicios activos.
    """
    catalogo = ServicioCatalogo.objects.filter(activo=True).order_by('nombre')
    serializer = ServicioCatalogoSerializer(catalogo, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(300)  # cachea 5 minutos la lista de tags públicos
def listar_tags(request):
    """
    Endpoint público para listar todos los tags disponibles.
    Los tags están organizados por categoría.
    """
    tags = Tag.objects.all().order_by('categoria', 'nombre')
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mis_likes(request):
    """Lista los perfiles a los que el cliente ha dado 'me gusta'. Solo clientes (no modelos)."""
    if request.user.es_modelo:
        return Response({"error": "Los modelos no usan likes de cliente"}, status=status.HTTP_403_FORBIDDEN)

    likes = PerfilLike.objects.filter(user=request.user).select_related('perfil_modelo')
    data = [
        {
            "perfil_id": like.perfil_modelo.id,
            "nombre_artistico": like.perfil_modelo.nombre_artistico,
            "foto_perfil": like.perfil_modelo.foto_perfil.url if like.perfil_modelo.foto_perfil else None,
        }
        for like in likes
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dar_like(request, id):
    """Marca like de un cliente sobre un perfil de modelo."""
    if request.user.es_modelo:
        return Response({"error": "Los modelos no pueden dar like"}, status=status.HTTP_403_FORBIDDEN)
    try:
        perfil = PerfilModelo.objects.get(id=id)
    except PerfilModelo.DoesNotExist:
        return Response({"error": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    PerfilLike.objects.get_or_create(user=request.user, perfil_modelo=perfil)
    return Response({"message": "Like registrado"}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def quitar_like(request, id):
    """Elimina el like de un cliente sobre un perfil de modelo."""
    if request.user.es_modelo:
        return Response({"error": "Los modelos no pueden dar like"}, status=status.HTTP_403_FORBIDDEN)
    PerfilLike.objects.filter(user=request.user, perfil_modelo_id=id).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsModeloUser])
def crear_perfil(request):
    """
    Crear perfil de modelo para el usuario autenticado.
    - Solo usuarios marcados como modelo (es_modelo=True) pueden usar este endpoint.
    - El perfil creado queda asociado siempre al request.user.
    """
    data = request.data.copy()
    # Compat: si envían 'ciudad' como nombre/ID, mapear a ciudad_id
    if 'ciudad_id' not in data and 'ciudad' in data:
        ciudad_val = data.get('ciudad')
        if isinstance(ciudad_val, str) and ciudad_val.isdigit():
            data['ciudad_id'] = ciudad_val
        else:
            try:
                ciudad_obj = Ciudad.objects.get(nombre__iexact=ciudad_val)
                data['ciudad_id'] = ciudad_obj.id
            except Ciudad.DoesNotExist:
                pass

    serializer = PerfilModeloSerializer(data=data)
    if serializer.is_valid():
        perfil = serializer.save(user=request.user)
        return Response(PerfilModeloSerializer(perfil, context={'request': request}).data, status=status.HTTP_201_CREATED)
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

    # Cooldown opcional: 7 días desde última solicitud aprobada o rechazada
    from django.utils import timezone
    cooldown_days = getattr(settings, "CAMBIO_CIUDAD_COOLDOWN_DAYS", 7)
    if cooldown_days:
        ultima = SolicitudCambioCiudad.objects.filter(perfil=perfil).order_by('-fecha_solicitud').first()
        if ultima and ultima.fecha_solicitud >= timezone.now() - timezone.timedelta(days=cooldown_days):
            return Response(
                {"error": f"Debes esperar {cooldown_days} días entre solicitudes de cambio de ciudad."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Crear la solicitud
    data = request.data.copy()
    data['perfil'] = perfil.id

    # Compat: aceptar ciudad_nueva o ciudad_nueva_id
    if 'ciudad_nueva_id' not in data:
        ciudad_val = data.get('ciudad_nueva')
        if ciudad_val:
            if isinstance(ciudad_val, str) and ciudad_val.isdigit():
                data['ciudad_nueva_id'] = ciudad_val
            else:
                try:
                    ciudad_obj = Ciudad.objects.get(nombre__iexact=ciudad_val)
                    data['ciudad_nueva_id'] = ciudad_obj.id
                except Ciudad.DoesNotExist:
                    pass
    serializer = SolicitudCambioCiudadSerializer(data=data)
    if serializer.is_valid():
        solicitud = serializer.save()
        
        # Send email notification to admin
        try:
            subject = 'Nueva Solicitud de Cambio de Ciudad'
            message = f"""
            Se ha creado una nueva solicitud de cambio de ciudad.
            
            Detalles:
            - Usuario: {perfil.user.username} ({perfil.user.email})
            - Nombre Artístico: {perfil.nombre_artistico or 'No especificado'}
            - Ciudad Actual: {perfil.ciudad}
            - Ciudad Solicitada: {solicitud.ciudad_nueva}
            - Fecha de Solicitud: {solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}
            
            Por favor, revisa y aprueba/rechaza esta solicitud en el panel de administración.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,  # No falla si el email no se puede enviar
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Error enviando email: {e}")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsProfileOwner])
def actualizar_perfil(request):
    """
    Endpoint para que una modelo actualice su perfil.
    Solo puede actualizar su propio perfil.
    El campo 'ciudad' NO puede ser actualizado - debe usar solicitud de cambio de ciudad.
    
    Campos actualizables:
    - foto_perfil
    - nombre_artistico
    - biografia
    - telefono_contacto
    - telegram_contacto
    - edad
    - genero
    - peso
    - altura
    - medidas
    - nacionalidad
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check object-level permission
    permission = IsProfileOwner()
    if not permission.has_object_permission(request, None, perfil):
        return Response(
            {"error": "No tienes permiso para actualizar este perfil"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Prevent ciudad updates through this endpoint
    if 'ciudad' in request.data:
        return Response(
            {"error": "No puedes cambiar la ciudad directamente. Usa el endpoint de solicitud de cambio de ciudad."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    partial = request.method == 'PATCH'
    serializer = PerfilModeloUpdateSerializer(perfil, data=request.data, partial=partial)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_tags(request):
    """
    Endpoint para que una modelo actualice sus tags.
    Solo puede actualizar los tags de su propio perfil.
    
    Body esperado:
    {
        "tag_ids": [1, 2, 3, 4]
    }
    
    O para limpiar todos los tags:
    {
        "tag_ids": []
    }
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    tag_ids = request.data.get('tag_ids', None)
    
    if tag_ids is None:
        return Response(
            {"error": "Se requiere el campo 'tag_ids' (lista de IDs de tags)"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not isinstance(tag_ids, list):
        return Response(
            {"error": "El campo 'tag_ids' debe ser una lista"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate that all tag IDs exist
    from .models import Tag
    existing_tags = Tag.objects.filter(id__in=tag_ids)
    
    if len(existing_tags) != len(tag_ids):
        invalid_ids = set(tag_ids) - set(existing_tags.values_list('id', flat=True))
        return Response(
            {"error": f"Tags con IDs {list(invalid_ids)} no existen"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update tags
    perfil.tags.set(tag_ids)
    
    # Return updated profile with tags
    serializer = PerfilModeloSerializer(perfil)
    return Response(
        {
            "message": "Tags actualizados correctamente",
            "tags": serializer.data['tags']
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsModeloUser])
def listar_mis_servicios(request):
    """
    Endpoint para que una modelo liste todos sus servicios.
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    servicios = Servicio.objects.filter(perfil_modelo=perfil)
    serializer = ServicioSerializer(servicios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsModeloUser])
def crear_servicio(request):
    """
    Endpoint para que una modelo cree un nuevo servicio.
    
    Body esperado:
    - catalogo_id (opcional si custom_text)
    - custom_text (opcional; requerido si no hay catalogo_id)
    
    Si el catalogo elegido no permite custom, custom_text debe ir vacío.
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    data = request.data.copy()
    data['perfil_modelo'] = perfil.id
    
    serializer = ServicioSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsModeloUser])
def actualizar_servicio(request, servicio_id):
    """
    Endpoint para que una modelo actualice uno de sus servicios.
    Solo puede actualizar sus propios servicios.
    
    Body esperado:
    {
        "nombre": "Servicio VIP Actualizado"
    }
    
    Nota: Los servicios solo incluyen nombres, no precios.
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        servicio = Servicio.objects.get(id=servicio_id, perfil_modelo=perfil)
    except Servicio.DoesNotExist:
        return Response(
            {"error": "Servicio no encontrado o no tienes permiso para editarlo"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    partial = request.method == 'PATCH'
    serializer = ServicioSerializer(servicio, data=request.data, partial=partial)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsModeloUser])
def eliminar_servicio(request, servicio_id):
    """
    Endpoint para que una modelo elimine uno de sus servicios.
    Solo puede eliminar sus propios servicios.
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        servicio = Servicio.objects.get(id=servicio_id, perfil_modelo=perfil)
    except Servicio.DoesNotExist:
        return Response(
            {"error": "Servicio no encontrado o no tienes permiso para eliminarlo"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    servicio.delete()
    return Response(
        {"message": "Servicio eliminado correctamente"},
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsModeloUser])
def listar_mis_fotos(request):
    """
    Endpoint para que una modelo liste todas sus fotos de galería.
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    fotos = GaleriaFoto.objects.filter(perfil_modelo=perfil)
    serializer = GaleriaFotoSerializer(fotos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsModeloUser])
def subir_foto(request):
    """
    Endpoint para que una modelo suba una nueva foto a su galería.
    
    Body esperado (multipart/form-data):
    - imagen: archivo de imagen
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if 'imagen' not in request.FILES:
        return Response(
            {"error": "Se requiere una imagen"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = {
        'perfil_modelo': perfil.id,
        'imagen': request.FILES['imagen']
    }
    
    serializer = GaleriaFotoSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsModeloUser])
def eliminar_foto(request, foto_id):
    """
    Endpoint para que una modelo elimine una foto de su galería.
    Solo puede eliminar sus propias fotos.
    """
    try:
        perfil = request.user.perfil_modelo
    except PerfilModelo.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil de modelo asociado"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        foto = GaleriaFoto.objects.get(id=foto_id, perfil_modelo=perfil)
    except GaleriaFoto.DoesNotExist:
        return Response(
            {"error": "Foto no encontrada o no tienes permiso para eliminarla"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Delete the image file from storage
    if foto.imagen:
        foto.imagen.delete(save=False)
    
    foto.delete()
    return Response(
        {"message": "Foto eliminada correctamente"},
        status=status.HTTP_204_NO_CONTENT
    )

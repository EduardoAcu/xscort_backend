from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import logging
from .models import Plan, Suscripcion, SolicitudSuscripcion
from .serializers import PlanSerializer, SuscripcionSerializer, SolicitudSuscripcionSerializer

logger = logging.getLogger('xscort')


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_planes(request):
    """
    Endpoint público para listar todos los planes disponibles.
    """
    planes = Plan.objects.all()
    serializer = PlanSerializer(planes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_renovar_suscripcion(request):
    """
    Endpoint para que la modelo cree o renueve su suscripción.
    Requiere: plan_id en el body.
    Lógica: dias_restantes += dias_contratados del plan.
    """
    plan_id = request.data.get('plan_id')
    
    if not plan_id:
        return Response({"error": "Se requiere plan_id"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        return Response({"error": "Plan no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    
    # Crear o obtener suscripción existente
    suscripcion, created = Suscripcion.objects.get_or_create(
        user=user,
        defaults={'plan': plan, 'dias_restantes': 0}
    )
    
    # Renovar/aumentar días
    suscripcion.plan = plan
    suscripcion.dias_restantes += plan.dias_contratados
    suscripcion.save()
    
    serializer = SuscripcionSerializer(suscripcion)
    mensaje = "Suscripción creada" if created else "Suscripción renovada"

    logger.info("Suscripción creada/renovada", extra={
        'user_id': user.id,
        'username': user.username,
        'plan_id': plan.id,
        'plan_nombre': plan.nombre,
        'dias_restantes': suscripcion.dias_restantes,
    })
    
    return Response({
        "mensaje": mensaje,
        "suscripcion": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pausar_suscripcion(request):
    """
    Endpoint para que una modelo pause su suscripción.
    Pone esta_pausada = True.
    
    Mientras esté pausada, el perfil no será visible públicamente.
    """
    user = request.user
    
    try:
        suscripcion = Suscripcion.objects.get(user=user)
    except Suscripcion.DoesNotExist:
        return Response(
            {"error": "No tienes una suscripción activa"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if already paused
    if suscripcion.esta_pausada:
        return Response(
            {"error": "Tu suscripción ya está pausada"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if there are remaining days
    if suscripcion.dias_restantes <= 0:
        return Response(
            {"error": "No puedes pausar una suscripción sin días restantes"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Pause subscription
    suscripcion.esta_pausada = True
    suscripcion.save()
    
    serializer = SuscripcionSerializer(suscripcion)
    
    return Response(
        {
            "mensaje": "Suscripción pausada exitosamente. Tu perfil no será visible hasta que la reactives.",
            "suscripcion": serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resumir_suscripcion(request):
    """
    Endpoint para que una modelo reanude/reactive su suscripción.
    Pone esta_pausada = False.
    
    Después de reanudar, el perfil volverá a ser visible públicamente.
    """
    user = request.user
    
    try:
        suscripcion = Suscripcion.objects.get(user=user)
    except Suscripcion.DoesNotExist:
        return Response(
            {"error": "No tienes una suscripción activa"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if already active (not paused)
    if not suscripcion.esta_pausada:
        return Response(
            {"error": "Tu suscripción ya está activa"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if there are remaining days
    if suscripcion.dias_restantes <= 0:
        return Response(
            {"error": "No puedes reanudar una suscripción sin días restantes. Por favor, renueva tu plan."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Resume subscription
    suscripcion.esta_pausada = False
    suscripcion.save()
    
    serializer = SuscripcionSerializer(suscripcion)
    
    return Response(
        {
            "mensaje": "Suscripción reactivada exitosamente. Tu perfil volverá a ser visible.",
            "suscripcion": serializer.data
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_suscripcion(request):
    """
    Endpoint para obtener la suscripción del usuario autenticado.
    """
    user = request.user
    
    try:
        suscripcion = Suscripcion.objects.get(user=user)
        serializer = SuscripcionSerializer(suscripcion)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Suscripcion.DoesNotExist:
        return Response(
            {"error": "No tienes una suscripción activa"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_solicitud_suscripcion(request):
    """Crea una solicitud de suscripción con comprobante de pago.

    Espera multipart/form-data con:
    - plan_id: ID del plan seleccionado
    - comprobante_pago: archivo de comprobante
    """
    user = request.user
    plan_id = request.data.get('plan_id')
    comprobante = request.FILES.get('comprobante_pago')

    if not plan_id:
        return Response({"error": "Se requiere plan_id"}, status=status.HTTP_400_BAD_REQUEST)
    if not comprobante:
        return Response({"error": "Se requiere comprobante_pago"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        return Response({"error": "Plan no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    solicitud = SolicitudSuscripcion.objects.create(
        user=user,
        plan=plan,
        comprobante_pago=comprobante,
    )

    serializer = SolicitudSuscripcionSerializer(solicitud)

    logger.info("Solicitud de suscripción creada", extra={
        'user_id': user.id,
        'username': user.username,
        'plan_id': plan.id,
        'plan_nombre': plan.nombre,
        'solicitud_id': solicitud.id,
    })

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mis_solicitudes_suscripcion(request):
    """Lista las solicitudes de suscripción del usuario autenticado."""
    user = request.user
    qs = SolicitudSuscripcion.objects.filter(user=user).order_by('-fecha_creacion')
    serializer = SolicitudSuscripcionSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aprobar_solicitud_suscripcion(request, solicitud_id):
    """
    Endpoint para que un admin apruebe una solicitud de suscripción y aplique el plan.
    """
    if not request.user.is_staff:
        return Response({"error": "Solo administradores"}, status=status.HTTP_403_FORBIDDEN)

    try:
        solicitud = SolicitudSuscripcion.objects.get(id=solicitud_id)
    except SolicitudSuscripcion.DoesNotExist:
        return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    solicitud.aplicar_plan()
    solicitud.estado = "aprobada"
    solicitud.save()

    serializer = SolicitudSuscripcionSerializer(solicitud)
    return Response(serializer.data, status=status.HTTP_200_OK)

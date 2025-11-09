from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Plan, Suscripcion
from .serializers import PlanSerializer, SuscripcionSerializer


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

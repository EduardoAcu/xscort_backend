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

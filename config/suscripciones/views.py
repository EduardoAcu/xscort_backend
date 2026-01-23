from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
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
    Endpoint MANUAL para crear/renovar suscripción (útil para pruebas o admin).
    Lógica: Extiende la fecha de expiración o reinicia el contador.
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
    suscripcion, created = Suscripcion.objects.get_or_create(user=user)
    
    # --- LÓGICA DE ACTUALIZACIÓN DE TIEMPO REAL ---
    # (Idéntica a SolicitudSuscripcion.aplicar_plan)
    
    now = timezone.now()
    dias_a_agregar = plan.dias_contratados
    suscripcion.plan = plan

    if suscripcion.esta_pausada:
        # Si está pausada, sumamos al "congelador"
        dias_actuales = suscripcion.dias_restantes if suscripcion.dias_restantes else 0
        suscripcion.dias_restantes = dias_actuales + dias_a_agregar
        # Opcional: Podrías despausar automáticamente aquí si quisieras
    else:
        # Si está activa o expirada
        if suscripcion.fecha_expiracion and suscripcion.fecha_expiracion > now:
            # Si está vigente, EXTENDEMOS la fecha actual
            suscripcion.fecha_expiracion += timedelta(days=dias_a_agregar)
        else:
            # Si es nueva o ya expiró, empieza desde HOY
            suscripcion.fecha_expiracion = now + timedelta(days=dias_a_agregar)

    suscripcion.save()
    
    serializer = SuscripcionSerializer(suscripcion)
    mensaje = "Suscripción creada" if created else "Suscripción renovada exitosamente"

    logger.info("Suscripción manual actualizada", extra={
        'user_id': user.id,
        'plan_id': plan.id,
        'nueva_expiracion': suscripcion.fecha_expiracion
    })
    
    return Response({
        "mensaje": mensaje,
        "suscripcion": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pausar_suscripcion(request):
    """
    Endpoint para pausar. Delega toda la lógica al modelo.
    """
    user = request.user
    
    try:
        suscripcion = Suscripcion.objects.get(user=user)
    except Suscripcion.DoesNotExist:
        return Response(
            {"error": "No tienes una suscripción activa"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if suscripcion.esta_pausada:
        return Response(
            {"error": "Tu suscripción ya está pausada"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar validez antes de pausar (opcional, el modelo también lo maneja)
    if not suscripcion.fecha_expiracion or suscripcion.fecha_expiracion <= timezone.now():
         return Response(
            {"error": "Tu suscripción ha expirado, no puedes pausarla."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # --- LLAMADA AL MÉTODO DEL MODELO ---
    suscripcion.pausar()
    
    serializer = SuscripcionSerializer(suscripcion)
    
    return Response(
        {
            "mensaje": "Suscripción pausada exitosamente. Tu tiempo restante se ha congelado.",
            "suscripcion": serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resumir_suscripcion(request):
    """
    Endpoint para reanudar. Delega toda la lógica al modelo.
    """
    user = request.user
    
    try:
        suscripcion = Suscripcion.objects.get(user=user)
    except Suscripcion.DoesNotExist:
        return Response(
            {"error": "No tienes una suscripción activa"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not suscripcion.esta_pausada:
        return Response(
            {"error": "Tu suscripción ya está activa"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # --- LLAMADA AL MÉTODO DEL MODELO ---
    suscripcion.reanudar()
    
    serializer = SuscripcionSerializer(suscripcion)
    
    return Response(
        {
            "mensaje": "Suscripción reactivada exitosamente. Tu perfil vuelve a ser visible.",
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
        # Usamos select_related para traer el plan en una sola consulta
        suscripcion = Suscripcion.objects.select_related('plan').get(user=user)
        
        # Opcional: Verificar si expiró para pausar/limpiar automáticamente 
        # (Aunque el serializer ya devuelve 0 días, a veces es útil limpiar estado)
        # if suscripcion.fecha_expiracion and suscripcion.fecha_expiracion < timezone.now():
        #     pass 

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
    """
    Crea una solicitud para que un admin la apruebe.
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

    logger.info("Solicitud creada", extra={'user': user.username, 'plan': plan.nombre})

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mis_solicitudes_suscripcion(request):
    """Lista las solicitudes del usuario."""
    user = request.user
    qs = SolicitudSuscripcion.objects.filter(user=user).order_by('-fecha_creacion')
    serializer = SolicitudSuscripcionSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aprobar_solicitud_suscripcion(request, solicitud_id):
    """
    Admin aprueba la solicitud.
    """
    if not request.user.is_staff:
        return Response({"error": "Solo administradores"}, status=status.HTTP_403_FORBIDDEN)

    try:
        solicitud = SolicitudSuscripcion.objects.get(id=solicitud_id)
    except SolicitudSuscripcion.DoesNotExist:
        return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if solicitud.estado == 'aprobada':
         return Response({"error": "Esta solicitud ya fue aprobada"}, status=status.HTTP_400_BAD_REQUEST)

    # La lógica pesada ahora vive en el modelo SolicitudSuscripcion
    solicitud.aplicar_plan()
    
    solicitud.estado = "aprobada"
    solicitud.save()

    serializer = SolicitudSuscripcionSerializer(solicitud)
    return Response(serializer.data, status=status.HTTP_200_OK)
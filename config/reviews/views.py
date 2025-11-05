from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Resena
from .serializers import ResenaSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_resena(request):
    """
    Endpoint para que un cliente autenticado (es_modelo=False) pueda crear una reseña.
    La reseña se crea con aprobada=False por defecto.
    """
    # Verificar que el usuario NO sea modelo
    if request.user.es_modelo:
        return Response(
            {"error": "Los modelos no pueden crear reseñas"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ResenaSerializer(data=request.data)
    
    if serializer.is_valid():
        # Asignar automáticamente el cliente autenticado
        serializer.save(cliente=request.user, aprobada=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

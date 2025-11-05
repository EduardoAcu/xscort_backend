from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import PerfilModelo
from .serializers import PerfilModeloSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def ver_perfil(request, id):
    """
    Endpoint público para ver un perfil de modelo por ID.
    Solo muestra perfiles con esta_verificada=True.
    """
    try:
        perfil = PerfilModelo.objects.get(id=id, user__esta_verificada=True)
        serializer = PerfilModeloSerializer(perfil)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except PerfilModelo.DoesNotExist:
        return Response({"error": "Perfil no encontrado o no verificado"}, status=status.HTTP_404_NOT_FOUND)


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

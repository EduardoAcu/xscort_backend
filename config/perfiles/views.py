from rest_framework import generics, permissions
from .models import PerfilModelo
from .serializers import PerfilModeloSerializer, PerfilModeloListSerializer


class PerfilModeloDetailView(generics.RetrieveAPIView):
    """
    API pública para ver el detalle de un perfil.
    GET /api/profiles/<id>/
    Solo muestra perfiles activos y verificados.
    """
    queryset = PerfilModelo.objects.filter(
        perfil_activo=True,
        user__esta_verificada=True
    )
    serializer_class = PerfilModeloSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'user'
    
    def retrieve(self, request, *args, **kwargs):
        # Incrementar visualizaciones
        instance = self.get_object()
        instance.visualizaciones += 1
        instance.save(update_fields=['visualizaciones'])
        return super().retrieve(request, *args, **kwargs)

# Nueva vista para listar perfiles públicos
class PerfilModeloListView(generics.ListAPIView):
    """
    API pública para listar perfiles.
    GET /api/profiles/
    Solo muestra perfiles activos y verificados.
    """
    queryset = PerfilModelo.objects.filter(
        perfil_activo=True,
        user__esta_verificada=True
    )
    serializer_class = PerfilModeloListSerializer
    permission_classes = [permissions.AllowAny]


from .models import SolicitudCambioCiudad


def solicitudes_pendientes(request):
    """
    Context processor to add pending city change requests count to all templates
    """
    if request.path.startswith('/admin/'):
        solicitudes_pendientes_count = SolicitudCambioCiudad.objects.filter(
            estado='pendiente'
        ).count()
        return {
            'solicitudes_pendientes_count': solicitudes_pendientes_count
        }
    return {}

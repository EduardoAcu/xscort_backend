from django.contrib import admin
from .models import PerfilModelo, Servicio, GaleriaFoto, Tag, SolicitudCambioCiudad

@admin.register(PerfilModelo)
class PerfilModeloAdmin(admin.ModelAdmin):
    list_display = ['nombre_artistico', 'ciudad', 'genero', 'edad']
    list_filter = ['genero', 'ciudad']
    search_fields = ['nombre_artistico', 'ciudad']
    filter_horizontal = ['tags']

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'perfil_modelo']
    list_filter = ['perfil_modelo']
    search_fields = ['nombre']

@admin.register(GaleriaFoto)
class GaleriaFotoAdmin(admin.ModelAdmin):
    list_display = ['perfil_modelo', 'imagen']
    list_filter = ['perfil_modelo']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria']
    list_filter = ['categoria']
    search_fields = ['nombre', 'categoria']

@admin.register(SolicitudCambioCiudad)
class SolicitudCambioCiudadAdmin(admin.ModelAdmin):
    list_display = ['perfil', 'ciudad_nueva', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'ciudad_nueva', 'fecha_solicitud']
    search_fields = ['perfil__nombre_artistico', 'perfil__user__email']
    readonly_fields = ['fecha_solicitud']
    actions = ['aprobar_cambios']
    
    @admin.action(description='Aprobar cambios de ciudad seleccionados')
    def aprobar_cambios(self, request, queryset):
        # Solo procesar solicitudes pendientes
        solicitudes_pendientes = queryset.filter(estado='pendiente')
        count = 0
        
        for solicitud in solicitudes_pendientes:
            # Actualizar el perfil con la nueva ciudad
            perfil = solicitud.perfil
            perfil.ciudad = solicitud.ciudad_nueva
            perfil.save()
            
            # Actualizar el estado de la solicitud
            solicitud.estado = 'aprobada'
            solicitud.save()
            
            count += 1
        
        self.message_user(
            request,
            f'{count} solicitud(es) aprobada(s) y ciudad(es) actualizada(s).',
        )

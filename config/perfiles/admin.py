from django.contrib import admin
from .models import (
    PerfilModelo, 
    Servicio, 
    GaleriaFoto, 
    Tag, 
    SolicitudCambioCiudad, 
    Ciudad, 
)

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activa', 'ordering']
    list_editable = ['activa', 'ordering'] # Edición rápida en la lista
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    # Ahora gestionas el catálogo aquí
    list_display = ['nombre', 'slug', 'activo', 'icono']
    list_editable = ['activo', 'icono']
    search_fields = ['nombre']
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'categoria']
    list_filter = ['categoria']
    search_fields = ['nombre']
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(PerfilModelo)
class PerfilModeloAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_artistico', 
        'user', 
        'ciudad', 
        'esta_publico', 
        'whatsapp'
    ]
    list_filter = ['esta_publico', 'ciudad', 'genero']
    search_fields = ['nombre_artistico', 'user__username', 'user__email', 'whatsapp']
    
    # CRÍTICO: Esto crea el selector cómodo para ManyToMany
    filter_horizontal = ['servicios', 'tags']
    
    # Rellena el slug basado en el nombre (aunque el modelo tiene lógica de backup)
    prepopulated_fields = {"slug": ("nombre_artistico",)}
    
    # Opcional: Para ver la foto en el admin
    def foto_preview(self, obj):
        if obj.foto_perfil:
            return f'<img src="{obj.foto_perfil.url}" width="50" />'
        return "-"


@admin.register(GaleriaFoto)
class GaleriaFotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'perfil_modelo', 'orden', 'es_publica']
    list_filter = ['es_publica', 'perfil_modelo']
    list_editable = ['orden', 'es_publica'] # Ordena fotos rápido sin entrar
    ordering = ['perfil_modelo', 'orden']


@admin.register(SolicitudCambioCiudad)
class SolicitudCambioCiudadAdmin(admin.ModelAdmin):
    list_display = ['perfil', 'ciudad_nueva', 'estado', 'fecha_solicitud']
    list_filter = ['estado', 'ciudad_nueva', 'fecha_solicitud']
    search_fields = ['perfil__nombre_artistico', 'perfil__user__email']
    readonly_fields = ['fecha_solicitud', 'fecha_resolucion']
    actions = ['aprobar_cambios', 'rechazar_cambios']
    
    @admin.action(description='Aprobar solicitudes seleccionadas')
    def aprobar_cambios(self, request, queryset):
        from django.utils import timezone
        
        pendientes = queryset.filter(estado='pendiente')
        count = 0
        
        for solicitud in pendientes:
            # 1. Actualizar el perfil
            perfil = solicitud.perfil
            perfil.ciudad = solicitud.ciudad_nueva
            perfil.save()
            
            # 2. Cerrar solicitud
            solicitud.estado = 'aprobada'
            solicitud.fecha_resolucion = timezone.now()
            solicitud.nota_admin = f"Aprobado por {request.user.username}"
            solicitud.save()
            count += 1
        
        self.message_user(request, f'{count} solicitudes aprobadas exitosamente.')

    @admin.action(description='Rechazar solicitudes seleccionadas')
    def rechazar_cambios(self, request, queryset):
        from django.utils import timezone
        rows = queryset.update(
            estado='rechazada', 
            fecha_resolucion=timezone.now(),
            nota_admin=f"Rechazado masivamente por {request.user.username}"
        )
        self.message_user(request, f'{rows} solicitudes rechazadas.')
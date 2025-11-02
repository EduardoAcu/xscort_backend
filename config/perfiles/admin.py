from django.contrib import admin
from .models import PerfilModelo, Servicio, GaleriaFoto, Tag


@admin.register(PerfilModelo)
class PerfilModeloAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'nombre_publico',
        'ciudad',
        'perfil_activo',
        'perfil_destacado',
        'tarifa_por_hora',
        'visualizaciones',
        'created_at'
    )
    list_filter = (
        'perfil_activo',
        'perfil_destacado',
        'acepta_visitas_domicilio',
        'acepta_encuentros_hotel',
        'ciudad'
    )
    search_fields = (
        'user__username',
        'user__email',
        'nombre_publico',
        'biografia',
        'ciudad',
        'telefono_trabajo',
        'telegram_usuario'
    )
    readonly_fields = ('created_at', 'updated_at', 'visualizaciones', 'ciudad')
    filter_horizontal = ('tags',)
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información Básica', {
            'fields': (
                'nombre_publico',
                'biografia',
                'telefono_trabajo',
                'telegram_usuario',
                'ciudad'
            )
        }),
        ('Información Física', {
            'fields': ('peso_kg', 'estatura_cm', 'medidas')
        }),
        ('Foto de Portada', {
            'fields': ('foto_portada',)
        }),
        ('Información Profesional', {
            'fields': ('tarifa_por_hora', 'servicios_ofrecidos', 'disponibilidad')
        }),
        ('Configuración de Encuentros', {
            'fields': ('acepta_visitas_domicilio', 'acepta_encuentros_hotel')
        }),
        ('Configuración de Perfil', {
            'fields': ('perfil_activo', 'perfil_destacado')
        }),
        ('Tags', {
            'fields': ('tags',)
        }),
        ('Estadísticas', {
            'fields': ('visualizaciones',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil', 'precio', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('nombre', 'perfil__user__username', 'perfil__nombre_publico')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información del Servicio', {
            'fields': ('perfil', 'nombre', 'precio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(GaleriaFoto)
class GaleriaFotoAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'imagen', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('perfil__user__username', 'perfil__nombre_publico')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información de la Foto', {
            'fields': ('perfil', 'imagen')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'created_at')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'categoria')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información del Tag', {
            'fields': ('nombre', 'categoria')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

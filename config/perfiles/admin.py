from django.contrib import admin
from .models import PerfilModelo, Servicio, GaleriaFoto, Tag

@admin.register(PerfilModelo)
class PerfilModeloAdmin(admin.ModelAdmin):
    list_display = ['nombre_artistico', 'ciudad', 'genero', 'edad']
    list_filter = ['genero', 'ciudad']
    search_fields = ['nombre_artistico', 'ciudad']
    filter_horizontal = ['tags']

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'perfil_modelo']
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

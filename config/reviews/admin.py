from django.contrib import admin
from .models import Resena


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'perfil_modelo', 'rating', 'aprobada', 'fecha_creacion']
    list_filter = ['aprobada', 'rating', 'fecha_creacion']
    search_fields = ['cliente__username', 'perfil_modelo__nombre_artistico', 'comentario']
    list_editable = ['aprobada']
    readonly_fields = ['fecha_creacion']
    ordering = ['-fecha_creacion']

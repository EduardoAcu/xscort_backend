from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Campos a mostrar en la lista de usuarios
    list_display = (
        'email', 'nombre_fantasia', 
        'verification_status', 'identity_verified', 'is_staff'
    )
    
    # Filtros en el panel lateral
    list_filter = (
        'verification_status', 'identity_verified',
        'email_verified', 'phone_verified', 'is_staff', 'is_active',
        'genero', 'ciudad'
    )
    
    # Campos de búsqueda
    search_fields = ('email', 'nombre_fantasia', 'telefono', 'document_number')
    
    # Organización de campos en el formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información del Perfil', {
            'fields': (
                'nombre_fantasia', 'genero', 'edad',
                'medidas', 'peso', 'altura', 'ciudad', 'telefono', 'biografia'
            )
        }),
        ('Verificación de Identidad', {
            'fields': (
                'email_verified', 'phone_verified', 'identity_verified',
                'verification_status', 'verified_at', 'rejection_reason'
            )
        }),
        ('Documentos', {
            'fields': (
                'document_type', 'document_number',
                'id_document_front', 'id_document_back', 'selfie'
            )
        }),
    )
    
    # Campos al crear un nuevo usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('email', 'nombre_fantasia')
        }),
    )

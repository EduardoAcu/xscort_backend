from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LegalDocument, AgeConsentLog


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Campos a mostrar en la lista de usuarios
    list_display = (
        'username', 'email', 'fecha_nacimiento', 'es_modelo', 'ha_solicitado_ser_modelo', 'esta_verificada', 'is_staff'
    )

    # Filtros en el panel lateral
    list_filter = (
        'es_modelo', 'ha_solicitado_ser_modelo', 'esta_verificada', 'is_staff', 'is_active', 'is_superuser'
    )

    # Campos de búsqueda
    search_fields = ('username', 'email', 'telefono_personal')

    # Organización de campos en el formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal', {
            'fields': (
                'fecha_nacimiento', 'telefono_personal'
            )
        }),
        ('Verificación de Modelo', {
            'fields': (
                'ha_solicitado_ser_modelo', 'es_modelo', 'esta_verificada',
                'foto_documento', 'selfie_con_documento'
            ),
            'description': 'Campos relacionados con la verificación para ser modelo. '
                          'Revisar documentos antes de aprobar.'
        }),
    )

    # Campos al crear un nuevo usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('email', 'fecha_nacimiento')
        }),
    )


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'version', 'is_current', 'created_at')
    list_filter = ('tipo', 'is_current')
    search_fields = ('version', 'body')


@admin.register(AgeConsentLog)
class AgeConsentLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'accepted_at', 'terms_version', 'privacy_version', 'ip_address')
    list_filter = ('terms_version', 'privacy_version')
    search_fields = ('user__username', 'user__email', 'ip_address', 'user_agent')

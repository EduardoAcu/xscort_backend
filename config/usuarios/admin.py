from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Campos a mostrar en la lista de usuarios
    list_display = (
        'username', 'email', 'es_modelo', 'esta_verificada', 'is_staff'
    )

    # Filtros en el panel lateral
    list_filter = (
        'es_modelo', 'esta_verificada', 'is_staff', 'is_active', 'is_superuser'
    )

    # Campos de búsqueda
    search_fields = ('username', 'email', 'telefono_personal')

    # Organización de campos en el formulario de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': (
                'es_modelo', 'telefono_personal', 'edad',
                'foto_documento', 'selfie_con_documento', 'esta_verificada'
            )
        }),
    )

    # Campos al crear un nuevo usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('email', 'es_modelo')
        }),
    )

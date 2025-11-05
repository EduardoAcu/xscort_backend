from django.contrib import admin
from .models import Plan, Suscripcion


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'dias_contratados']
    search_fields = ['nombre']


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'dias_restantes', 'esta_pausada', 'fecha_actualizacion']
    list_filter = ['esta_pausada', 'plan']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['fecha_inicio', 'fecha_actualizacion']

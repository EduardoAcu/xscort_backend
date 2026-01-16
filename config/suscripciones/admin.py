from django.contrib import admin
from .models import Plan, Suscripcion, SolicitudSuscripcion


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


@admin.register(SolicitudSuscripcion)
class SolicitudSuscripcionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'plan', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'plan']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    def save_model(self, request, obj, form, change):
        """Cuando una solicitud pasa a 'aprobada', activa la suscripción del usuario.

        Solo aplica la activación cuando el estado cambia de algo distinto de 'aprobada'
        a 'aprobada', para evitar sumar días duplicados.
        """
        old_estado = None
        if change:
            try:
                old = SolicitudSuscripcion.objects.get(pk=obj.pk)
                old_estado = old.estado
            except SolicitudSuscripcion.DoesNotExist:
                old_estado = None

        super().save_model(request, obj, form, change)

        if obj.estado == 'aprobada' and old_estado != 'aprobada':
            obj.aplicar_plan()

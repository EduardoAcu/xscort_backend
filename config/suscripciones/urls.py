from django.urls import path
from . import views

app_name = 'suscripciones'

urlpatterns = [
    path('', views.obtener_suscripcion, name='obtener_suscripcion'),
    path('mi-suscripcion/', views.obtener_suscripcion, name='mi_suscripcion'),  # alias
    path('planes/', views.listar_planes, name='listar_planes'),
    path('suscribir/', views.crear_renovar_suscripcion, name='crear_renovar_suscripcion'),
    path('pausar/', views.pausar_suscripcion, name='pausar_suscripcion'),
    path('resumir/', views.resumir_suscripcion, name='resumir_suscripcion'),
    path('solicitudes/', views.crear_solicitud_suscripcion, name='crear_solicitud_suscripcion'),
    path('solicitudes/mias/', views.listar_mis_solicitudes_suscripcion, name='listar_mis_solicitudes_suscripcion'),
    path('solicitudes/<int:solicitud_id>/aprobar/', views.aprobar_solicitud_suscripcion, name='aprobar_solicitud_suscripcion'),
]

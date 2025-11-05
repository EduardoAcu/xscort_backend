from django.urls import path
from . import views

app_name = 'suscripciones'

urlpatterns = [
    path('planes/', views.listar_planes, name='listar_planes'),
    path('suscribir/', views.crear_renovar_suscripcion, name='crear_renovar_suscripcion'),
    path('pausar/', views.pausar_suscripcion, name='pausar_suscripcion'),
    path('resumir/', views.resumir_suscripcion, name='resumir_suscripcion'),
]

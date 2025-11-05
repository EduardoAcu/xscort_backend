from django.urls import path
from . import views

app_name = 'suscripciones'

urlpatterns = [
    path('planes/', views.listar_planes, name='listar_planes'),
    path('suscribir/', views.crear_renovar_suscripcion, name='crear_renovar_suscripcion'),
]

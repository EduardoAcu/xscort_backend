from django.urls import path
from . import views

app_name = 'perfiles'

urlpatterns = [
    path('', views.listar_perfiles, name='listar_perfiles'),
    path('<int:id>/', views.ver_perfil, name='ver_perfil'),
    path('create/', views.crear_perfil, name='crear_perfil'),
    path('solicitar-cambio-ciudad/', views.solicitar_cambio_ciudad, name='solicitar_cambio_ciudad'),
]

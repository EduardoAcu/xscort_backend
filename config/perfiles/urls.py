from django.urls import path
from . import views

app_name = 'perfiles'

urlpatterns = [
    path('', views.listar_perfiles, name='listar_perfiles'),
    path('tags/', views.listar_tags, name='listar_tags'),
    path('<int:id>/', views.ver_perfil, name='ver_perfil'),
    path('create/', views.crear_perfil, name='crear_perfil'),
    path('mi-perfil/actualizar/', views.actualizar_perfil, name='actualizar_perfil'),
    path('mi-perfil/actualizar-tags/', views.actualizar_tags, name='actualizar_tags'),
    path('solicitar-cambio-ciudad/', views.solicitar_cambio_ciudad, name='solicitar_cambio_ciudad'),
    
    # Servicios CRUD
    path('mis-servicios/', views.listar_mis_servicios, name='listar_mis_servicios'),
    path('mis-servicios/crear/', views.crear_servicio, name='crear_servicio'),
    path('mis-servicios/<int:servicio_id>/actualizar/', views.actualizar_servicio, name='actualizar_servicio'),
    path('mis-servicios/<int:servicio_id>/eliminar/', views.eliminar_servicio, name='eliminar_servicio'),
    
    # Galería CRUD
    path('mi-galeria/', views.listar_mis_fotos, name='listar_mis_fotos'),
    path('mi-galeria/subir/', views.subir_foto, name='subir_foto'),
    path('mi-galeria/<int:foto_id>/eliminar/', views.eliminar_foto, name='eliminar_foto'),
]

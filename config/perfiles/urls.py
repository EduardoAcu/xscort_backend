from django.urls import path
from . import views

app_name = 'perfiles'

urlpatterns = [
    # --- 1. CATÁLOGOS PÚBLICOS ---
    path('ciudades/', views.CiudadListView.as_view(), name='listar_ciudades'),
    path('servicios/', views.ServicioListView.as_view(), name='listar_servicios'),
    path('tags/', views.TagListView.as_view(), name='listar_tags'),
    path('servicios-catalogo/', views.ServicioCatalogoView.as_view(), name='servicios-catalogo'),

    # --- 2. GESTIÓN PRIVADA (¡ESTO DEBE IR PRIMERO!) ---
    # Al poner esto arriba, Django revisa si es "mi-perfil" ANTES de pensar que es un slug
    path('mi-perfil/', views.MiPerfilView.as_view(), name='mi_perfil'),
    path('mi-galeria/', views.MiGaleriaView.as_view(), name='mi_galeria'),
    path('mi-galeria/<int:pk>/', views.GaleriaDetailView.as_view(), name='eliminar_foto'),
    path('solicitar-cambio-ciudad/', views.SolicitudCambioCiudadCreateView.as_view(), name='solicitar_cambio_ciudad'),
    

    # --- 3. PERFILES PÚBLICOS ---
    path('', views.PerfilModeloListView.as_view(), name='listar_perfiles'),
    
    # INTERACCIONES
    path('<int:perfil_id>/like/', views.ToggleLikeView.as_view(), name='toggle_like'),
    path('likes/', views.MisLikesView.as_view(), name='listar_mis_likes'),

    # --- 4. DETALLE POR SLUG (¡ESTO DEBE IR AL FINAL!) ---
    # Esta ruta atrapa "cualquier cosa". Si la pones arriba, se come a las demás.
    path('<slug:slug>/', views.PerfilModeloDetailView.as_view(), name='ver_perfil'),
]
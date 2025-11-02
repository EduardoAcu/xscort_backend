from django.urls import path
from .views import PerfilModeloListView, PerfilModeloDetailView

app_name = 'perfiles'

urlpatterns = [
    path('profiles/', PerfilModeloListView.as_view(), name='perfil-list'),
    path('profiles/<int:user>/', PerfilModeloDetailView.as_view(), name='perfil-detail'),
]

from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('crear/', views.crear_resena, name='crear_resena'),
]

import django_filters
from .models import PerfilModelo

class PerfilFilter(django_filters.FilterSet):
    # Filtramos por el 'slug' de la relación ciudad
    ciudad = django_filters.CharFilter(field_name='ciudad__slug', lookup_expr='iexact')
    
    # Filtramos por el 'slug' de los servicios (tags)
    servicio = django_filters.CharFilter(field_name='servicios__slug', lookup_expr='iexact')
    
    # Filtramos por tags generales
    tags = django_filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')

    class Meta:
        model = PerfilModelo
        fields = ['ciudad', 'servicio', 'tags', 'genero', 'esta_publico']
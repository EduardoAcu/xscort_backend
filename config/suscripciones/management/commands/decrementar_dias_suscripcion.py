from django.core.management.base import BaseCommand
from suscripciones.models import Suscripcion


class Command(BaseCommand):
    help = 'Decrementa dias_restantes en 1 para suscripciones activas y no pausadas'

    def handle(self, *args, **options):
        # Buscar suscripciones activas y no pausadas
        suscripciones = Suscripcion.objects.filter(
            dias_restantes__gt=0,
            esta_pausada=False
        )
        
        count = 0
        for suscripcion in suscripciones:
            suscripcion.dias_restantes -= 1
            suscripcion.save()
            count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Se decrementaron {count} suscripciones exitosamente'
            )
        )

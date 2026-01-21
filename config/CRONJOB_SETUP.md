# Configuración del Cronjob para Decrementar Días de Suscripción

## Comando Django Creado

Se ha creado el comando de gestión: `decrementar_dias_suscripcion`

**Ubicación:** `suscripciones/management/commands/decrementar_dias_suscripcion.py`

**Función:** Decrementa `dias_restantes` en 1 para todas las suscripciones donde:
- `dias_restantes > 0`
- `esta_pausada = False`

## Probar el Comando

```bash
python manage.py decrementar_dias_suscripcion
```

## Configuración del Cronjob

### Opción 1: Usar crontab del sistema (Linux/macOS)

1. Abrir el crontab:
```bash
crontab -e
```

2. Agregar la siguiente línea para ejecutar diariamente a las 00:00:
```bash
0 0 * * * cd /Users/eduardo/Documents/GitHub/xscort_backend/config && /usr/local/bin/python manage.py decrementar_dias_suscripcion >> /tmp/decrementar_suscripciones.log 2>&1
```

**Nota:** Ajustar la ruta de Python según tu entorno (puede ser `/usr/bin/python3` o la ruta de tu virtualenv)

### Opción 2: Usar django-crontab (Recomendado)

1. Instalar django-crontab:
```bash
pip install django-crontab
```

2. Agregar a `INSTALLED_APPS` en `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'django_crontab',
]
```

3. Agregar al final de `settings.py`:
```python
CRONJOBS = [
    ('0 0 * * *', 'django.core.management.call_command', ['decrementar_dias_suscripcion']),
]
```

4. Agregar el cronjob:
```bash
python manage.py crontab add
```

5. Ver cronjobs activos:
```bash
python manage.py crontab show
```

6. Remover cronjobs (si es necesario):
```bash
python manage.py crontab remove
```

### Opción 3: Usar Celery Beat (Para producción)

1. Instalar Celery:
```bash
pip install celery redis
```

2. Configurar en `settings.py` y crear tareas periódicas

## Verificación

Para verificar que el cronjob está funcionando, revisar el log:
```bash
tail -f /tmp/decrementar_suscripciones.log
```

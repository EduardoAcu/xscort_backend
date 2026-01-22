import environ
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url

# 1. INICIALIZACIÓN DE ENTORNO
env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Leer .env solo si existe (Desarrollo local)
if os.path.exists(os.path.join(BASE_DIR, '.env')):
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 2. CONFIGURACIÓN BÁSICA
DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')

# Dominios permitidos
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['api.xscort.cl', 'localhost', '127.0.0.1'])

# 3. DEFINICIÓN DE APLICACIONES
INSTALLED_APPS = [
    'jazzmin',  # Debe ir antes de admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Librerías de Terceros
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'storages',  # Para Cloudflare R2
    
    # Tus Aplicaciones
    'usuarios',
    'perfiles',
    'suscripciones',
    'reviews',
]

# 4. MIDDLEWARE (El orden es vital)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Manejo de archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'usuarios.middleware.JWTAuthCookieMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'perfiles.context_processors.solicitudes_pendientes',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# 5. BASE DE DATOS (PostgreSQL en Coolify / SQLite en Local)
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# 6. ARCHIVOS ESTÁTICOS Y MULTIMEDIA
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'config', 'staticfiles')
# Whitenoise: Compresión y caché
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True 
WHITENOISE_MANIFEST_STRICT = False 

# Configuración de Almacenamiento en la Nube (Cloudflare R2)
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default=None)

# settings.py

if AWS_ACCESS_KEY_ID:
    # 1. Credenciales (Las toma de Coolify)
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')

    # 2. Endpoint LIMPIO (Sin el nombre del bucket al final)
    AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')

    # 3. Configuración obligatoria para R2
    AWS_S3_REGION_NAME = 'auto'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False  # Importante: URLs públicas sin tokens raros

    # 4. Dominio Personalizado
    AWS_S3_CUSTOM_DOMAIN = 'media.xscort.cl'

    # 5. Almacenamiento
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://media.xscort.cl/'

else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 7. SEGURIDAD Y CORS
AUTH_USER_MODEL = 'usuarios.CustomUser'

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'https://xscort.cl',
    'http://localhost:3000',
])

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://api.xscort.cl',
    'https://xscort.cl'
])

CORS_ALLOW_CREDENTIALS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 8. DJANGO REST FRAMEWORK & JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60)),
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# 9. CONFIGURACIÓN DE EMAIL (SMTP)
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.resend.com') # Recomendado
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'resend'
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@xscort.cl')

# 10. INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'es-ES'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Importar Jazzmin Config al final
from .jazzmin_config import *
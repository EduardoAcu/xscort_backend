# Configuración de Variables de Entorno

Este proyecto utiliza variables de entorno para toda su configuración. Esto permite mantener configuraciones sensibles fuera del código y facilita el despliegue en diferentes ambientes.

## Setup Inicial

### 1. Copiar el archivo de ejemplo

```bash
cp .env.example .env
```

### 2. Generar SECRET_KEY

Genera una nueva SECRET_KEY para Django:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copia el resultado y pégalo en tu archivo `.env`:

```
SECRET_KEY=tu-secret-key-generada-aqui
```

### 3. Configurar variables básicas

Edita el archivo `.env` con tus configuraciones:

```bash
nano .env  # o usa tu editor preferido
```

## Variables Disponibles

### Django Core

| Variable | Descripción | Valores | Default |
|----------|-------------|---------|---------|
| `SECRET_KEY` | Llave secreta de Django (REQUERIDO) | String único | - |
| `DEBUG` | Modo debug | `True`, `False` | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | `localhost,127.0.0.1` | `localhost,127.0.0.1` |

### Base de Datos

#### SQLite (Development)
```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

#### PostgreSQL (Production)
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=xscort_db
DB_USER=xscort_user
DB_PASSWORD=tu_password_segura
DB_HOST=localhost
DB_PORT=5432
```

#### MySQL (Alternative)
```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=xscort_db
DB_USER=xscort_user
DB_PASSWORD=tu_password_segura
DB_HOST=localhost
DB_PORT=3306
```

### Archivos Estáticos y Media

| Variable | Descripción | Default |
|----------|-------------|---------|
| `STATIC_URL` | URL para archivos estáticos | `/static/` |
| `STATIC_ROOT` | Directorio para collectstatic | `staticfiles` |
| `MEDIA_URL` | URL para archivos subidos | `/media/` |
| `MEDIA_ROOT` | Directorio para archivos subidos | `media` |

### JWT Authentication

| Variable | Descripción | Default |
|----------|-------------|---------|
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Duración del access token (minutos) | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Duración del refresh token (días) | `1` |

### Email

#### Development (Console)
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### Production (Gmail)
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=noreply@xscort.com
ADMIN_EMAIL=admin@xscort.com
```

**Nota para Gmail:** Necesitas crear una "App Password":
1. Ve a https://myaccount.google.com/security
2. Activa 2FA (si no está activado)
3. Ve a "App Passwords"
4. Genera una contraseña para "Mail"
5. Usa esa contraseña en `EMAIL_HOST_PASSWORD`

#### Production (SendGrid)
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=tu-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@xscort.com
ADMIN_EMAIL=admin@xscort.com
```

### CORS

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `CORS_ALLOWED_ORIGINS` | Orígenes permitidos (con protocolo, separados por coma) | `http://localhost:3000,https://xscort.cl` |
| `CORS_ALLOW_CREDENTIALS` | Permitir credenciales | `True`, `False` |

## Configuraciones por Ambiente

### Development (.env)

```env
SECRET_KEY=django-insecure-dev-key-change-in-prod
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
ADMIN_EMAIL=dev@localhost

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=True

JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1
```

### Production (.env)

```env
SECRET_KEY=tu-secret-key-super-segura-generada
DEBUG=False
ALLOWED_HOSTS=xscort.cl,www.xscort.cl,api.xscort.cl

# PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=xscort_production
DB_USER=xscort_prod_user
DB_PASSWORD=password-super-segura-aqui
DB_HOST=localhost
DB_PORT=5432

# Static/Media (usar con S3 o similar en producción real)
STATIC_URL=/static/
STATIC_ROOT=/var/www/xscort/static
MEDIA_URL=/media/
MEDIA_ROOT=/var/www/xscort/media

# Email (SendGrid)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@xscort.com
ADMIN_EMAIL=admin@xscort.com

# CORS
CORS_ALLOWED_ORIGINS=https://xscort.cl,https://www.xscort.cl
CORS_ALLOW_CREDENTIALS=True

# JWT (tokens más cortos en producción)
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

## Verificar Configuración

Después de configurar tu `.env`, verifica que todo esté correcto:

```bash
cd config
python manage.py check
```

Si hay errores de configuración, Django te lo indicará.

## Migraciones Iniciales

```bash
cd config
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## Ejecutar el Servidor

```bash
cd config
python manage.py runserver
```

## Seguridad

### ⚠️ IMPORTANTE

1. **NUNCA** commitees el archivo `.env` al repositorio
2. El archivo `.env` ya está en `.gitignore`
3. En producción, usa `DEBUG=False`
4. Genera un `SECRET_KEY` único para cada ambiente
5. Usa contraseñas fuertes para la base de datos
6. Considera usar servicios como AWS Secrets Manager o similar para producción

### Generar SECRET_KEY segura

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Troubleshooting

### Error: "SECRET_KEY not found"
- Asegúrate de que el archivo `.env` existe en la raíz del proyecto
- Verifica que la variable `SECRET_KEY` está definida

### Error: CORS
- Verifica que los orígenes incluyan el protocolo (`http://` o `https://`)
- No uses espacios después de las comas en listas

### Error: Database
- Para PostgreSQL, asegúrate de que el servidor está corriendo
- Verifica usuario/password/host/port
- Para SQLite, asegúrate de que el directorio tiene permisos de escritura

### Error: Email
- En desarrollo, usa `console.EmailBackend`
- En producción, verifica credenciales SMTP
- Para Gmail, usa App Password, no tu contraseña normal

## Ejemplo Completo Funcional

Crea tu `.env` copiando este ejemplo y ajustando valores:

```env
# Core
SECRET_KEY=django-insecure-tu-key-aqui-cambiar-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite para desarrollo)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Files
STATIC_URL=/static/
STATIC_ROOT=staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=media

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1

# Email (Console para desarrollo)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
ADMIN_EMAIL=admin@localhost

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=True
```

Guarda y ejecuta:

```bash
cd config
python manage.py migrate
python manage.py runserver
```

¡Listo! El backend debería estar funcionando en http://localhost:8000

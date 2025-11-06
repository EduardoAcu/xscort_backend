# Xscort Backend

Backend API para la plataforma Xscort - Sistema de gestión de perfiles de modelos con autenticación, suscripciones, y sistema de verificación.

## 🚀 Stack Tecnológico

- **Framework**: Django 5.2 + Django REST Framework
- **Autenticación**: JWT (Simple JWT)
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Admin Panel**: Django Jazzmin
- **CORS**: django-cors-headers
- **Cron Jobs**: django-crontab

## 📋 Prerequisitos

- Python 3.10+
- pip
- virtualenv (recomendado)

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd xscort_backend
```

### 2. Crear y activar entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Generar SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Editar .env con tu SECRET_KEY y otras configuraciones
nano .env
```

Ver [ENV_SETUP.md](ENV_SETUP.md) para documentación detallada de todas las variables de entorno.

### 5. Aplicar migraciones

```bash
cd config
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Crear datos iniciales (opcional)

```bash
# Crear tags
python manage.py shell
>>> from perfiles.models import Tag
>>> Tag.objects.create(nombre="Rubia", categoria="Apariencia")
>>> Tag.objects.create(nombre="Morena", categoria="Apariencia")
>>> Tag.objects.create(nombre="Masajes", categoria="Servicios")
>>> exit()

# Crear planes de suscripción
python manage.py shell
>>> from suscripciones.models import Plan
>>> Plan.objects.create(nombre="Plan Básico", precio=10000, dias_contratados=30)
>>> Plan.objects.create(nombre="Plan Premium", precio=25000, dias_contratados=90)
>>> exit()
```

### 8. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

El servidor estará disponible en `http://localhost:8000`

## 📚 API Endpoints

### Usuarios

- `POST /api/register/` - Registro de usuario
- `POST /api/token/` - Login y obtención de tokens JWT
- `POST /api/verification/upload-documents/` - Subir documentos de verificación

### Perfiles

- `GET /api/profiles/` - Listar perfiles públicos (con filtros)
- `GET /api/profiles/tags/` - Listar tags disponibles
- `GET /api/profiles/{id}/` - Ver perfil específico
- `POST /api/profiles/create/` - Crear perfil de modelo
- `PATCH /api/profiles/mi-perfil/actualizar/` - Actualizar mi perfil
- `PUT /api/profiles/mi-perfil/actualizar-tags/` - Actualizar mis tags
- `POST /api/profiles/solicitar-cambio-ciudad/` - Solicitar cambio de ciudad

### Servicios

- `GET /api/profiles/mis-servicios/` - Listar mis servicios
- `POST /api/profiles/mis-servicios/crear/` - Crear servicio
- `PATCH /api/profiles/mis-servicios/{id}/actualizar/` - Actualizar servicio
- `DELETE /api/profiles/mis-servicios/{id}/eliminar/` - Eliminar servicio

### Galería

- `GET /api/profiles/mi-galeria/` - Listar mis fotos
- `POST /api/profiles/mi-galeria/subir/` - Subir foto
- `DELETE /api/profiles/mi-galeria/{id}/eliminar/` - Eliminar foto

### Suscripciones

- `GET /api/subscriptions/planes/` - Listar planes
- `POST /api/subscriptions/suscribir/` - Crear/renovar suscripción
- `POST /api/subscriptions/pausar/` - Pausar suscripción
- `POST /api/subscriptions/resumir/` - Reactivar suscripción

Ver [API_TESTS.md](API_TESTS.md) para ejemplos completos de uso.

## 🔐 Autenticación

La API usa JWT (JSON Web Tokens). Para endpoints protegidos:

```bash
# 1. Obtener token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tu_usuario","password":"tu_password"}'

# 2. Usar token en requests
curl -X GET http://localhost:8000/api/profiles/mis-servicios/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🛠️ Administración

### Django Admin

Accede al panel de administración en `http://localhost:8000/admin/`

Características:
- Dashboard con alertas de solicitudes pendientes
- Gestión de usuarios y verificaciones
- Aprobación de cambios de ciudad
- Gestión de planes, tags y suscripciones

### Tareas Cron

El sistema incluye un cron job para decrementar días de suscripción:

```bash
# Agregar cron jobs
python manage.py crontab add

# Ver cron jobs activos
python manage.py crontab show

# Remover cron jobs
python manage.py crontab remove
```

## 🧪 Testing

```bash
cd config

# Ejecutar tests
python manage.py test

# Tests específicos
python manage.py test perfiles
python manage.py test usuarios
```

Ver [API_TESTS.md](API_TESTS.md) para pruebas manuales completas.

## 📁 Estructura del Proyecto

```
xscort_backend/
├── config/                  # Directorio principal del proyecto
│   ├── config/             # Configuración Django
│   │   ├── settings.py    # Configuración principal
│   │   ├── urls.py        # URLs principales
│   │   └── jazzmin_config.py
│   ├── usuarios/          # App de usuarios
│   ├── perfiles/          # App de perfiles de modelos
│   ├── suscripciones/     # App de suscripciones
│   ├── reviews/           # App de reseñas
│   ├── moderation/        # App de moderación
│   └── manage.py          # CLI de Django
├── .env                   # Variables de entorno (NO commitear)
├── .env.example           # Template de variables
├── .gitignore            # Archivos ignorados por git
├── requirements.txt      # Dependencias Python
├── README.md            # Este archivo
├── ENV_SETUP.md         # Guía de configuración
└── API_TESTS.md         # Pruebas de API
```

## 🚢 Despliegue

### Configuración de Producción

1. **Variables de entorno**:
   ```env
   DEBUG=False
   SECRET_KEY=<generar-nueva-key>
   ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
   ```

2. **Base de datos**: Cambiar a PostgreSQL
   ```env
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=xscort_production
   DB_USER=xscort_user
   DB_PASSWORD=password_segura
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. **Archivos estáticos**:
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Email**: Configurar SMTP real (Gmail, SendGrid, etc.)

5. **CORS**: Actualizar orígenes permitidos
   ```env
   CORS_ALLOWED_ORIGINS=https://tu-dominio.com
   ```

Ver [ENV_SETUP.md](ENV_SETUP.md) para configuración completa de producción.

## 🔒 Seguridad

- ✅ `.env` está en `.gitignore`
- ✅ Autenticación JWT
- ✅ Permisos por endpoint
- ✅ CORS configurado
- ✅ Validación de datos en serializers
- ✅ Ownership validation en updates/deletes

**IMPORTANTE**:
- Nunca commitees el archivo `.env`
- Usa `DEBUG=False` en producción
- Genera una `SECRET_KEY` única
- Usa contraseñas fuertes para BD
- Configura HTTPS en producción

## 🐛 Troubleshooting

### Error: SECRET_KEY not found
```bash
# Verifica que .env existe y tiene SECRET_KEY
ls -la .env
grep SECRET_KEY .env
```

### Error: CORS
```bash
# Asegúrate de incluir protocolo en CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS=https://dominio.com  # ✅ Correcto
CORS_ALLOWED_ORIGINS=dominio.com          # ❌ Incorrecto
```

### Error: Database
```bash
# Para SQLite, verifica permisos
ls -l db.sqlite3

# Para PostgreSQL, verifica conexión
psql -U xscort_user -d xscort_db -h localhost
```

Ver [ENV_SETUP.md](ENV_SETUP.md) para más soluciones.

## 📖 Documentación Adicional

- [ENV_SETUP.md](ENV_SETUP.md) - Configuración de variables de entorno
- [API_TESTS.md](API_TESTS.md) - Pruebas y ejemplos de uso de API
- [WARP.md](config/WARP.md) - Guía para desarrollo con Warp

## 🤝 Contribución

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

[Especificar licencia]

## 👥 Contacto

Eduardo - [tu-email@dominio.com]

Project Link: [https://github.com/tu-usuario/xscort_backend](https://github.com/tu-usuario/xscort_backend)

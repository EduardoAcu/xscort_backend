# Análisis Completo del Backend - Xscort

**Fecha:** 10 de noviembre, 2025
**Proyecto:** xscort_backend (Django)

---

## 📋 RESUMEN EJECUTIVO

He analizado el código del backend y encontré varios problemas importantes que necesitan corrección, así como oportunidades de mejora en la arquitectura del sistema.

---

## 🔍 ANÁLISIS POR ÁREA

### 1. ❌ PROBLEMA CRÍTICO: Flujo de Registro y Verificación

#### **Estado Actual:**
El flujo de registro NO cumple con los requerimientos de seguridad y validación de edad:

**Problemas identificados:**

1. **No hay validación de mayoría de edad obligatoria:**
   - El modelo `CustomUser` NO tiene un campo `fecha_nacimiento` o similar
   - No se valida que el usuario tenga 18+ años al registrarse
   - Solo se verifica documentos DESPUÉS de registrarse como modelo

2. **Flujo de verificación inconsistente:**
   ```
   Flujo ACTUAL (INCORRECTO):
   Usuario se registra → Opcionalmente se marca como modelo → Sube documentos → Admin verifica
   
   Flujo REQUERIDO (CORRECTO):
   Usuario se registra → Sube documentos de verificación (OBLIGATORIO) → 
   Admin verifica mayoría de edad → Solo entonces puede crear perfil de modelo público
   ```

3. **El endpoint `become-model` es problemático:**
   - Permite que cualquier usuario se marque como modelo sin verificación previa
   - No requiere validación de documentos primero
   - Ubicación: `usuarios/views.py:131-144`

#### **Código problemático:**
```python path=/Users/eduardo/Documents/GitHub/xscort_backend/config/usuarios/views.py start=131
class BecomeModelView(APIView):
    def post(self, request):
        user = request.user
        if user.es_modelo:
            return Response({"message": "Ya eres modelo"}, status=status.HTTP_200_OK)
        user.es_modelo = True  # ❌ No hay validación de documentos ni edad
        user.save()
        return Response({{"message": "Habilitada como modelo"}, status=status.HTTP_200_OK)
```

#### **Solución Recomendada:**

**A. Agregar campo de fecha de nacimiento:**
```python
# En usuarios/models.py
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)  # NUEVO
    es_modelo = models.BooleanField(default=False)
    # ... resto de campos
```

**B. Modificar flujo de registro:**
- El registro debe solicitar fecha de nacimiento
- Validar que sea mayor de 18 años
- NO permitir que el usuario se marque como modelo hasta pasar verificación

**C. Modificar flujo de verificación:**
```python
# Nuevo flujo propuesto:
1. Usuario se registra con fecha_nacimiento (validar 18+)
2. Usuario solicita ser modelo (nuevo endpoint)
3. Usuario DEBE subir documentos de verificación
4. Admin revisa documentos y fecha de nacimiento
5. Solo si aprueba: esta_verificada = True Y es_modelo = True
6. El usuario puede crear su perfil público de modelo
```

**D. Eliminar o modificar `BecomeModelView`:**
- Eliminar el endpoint actual `/api/become-model/`
- Crear un nuevo endpoint `/api/request-model-verification/` que:
  - Requiera subida de documentos en la misma llamada
  - No active `es_modelo` inmediatamente
  - Cree una solicitud pendiente de verificación

---

### 2. ⚠️ PROBLEMA: App de Servicios - Incluye Precios

#### **Estado Actual:**
La app de servicios actualmente incluye precios, lo cual NO es lo deseado según los requerimientos.

**Ubicación del problema:**
```python path=/Users/eduardo/Documents/GitHub/xscort_backend/config/perfiles/models.py start=55
class Servicio(models.Model):
    perfil_modelo = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # ❌ ELIMINAR
```

#### **Solución Recomendada:**

**A. Eliminar campo precio del modelo:**
```python
class Servicio(models.Model):
    perfil_modelo = models.ForeignKey(PerfilModelo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    # precio eliminado
```

**B. Actualizar serializer:**
```python
# En perfiles/serializers.py
class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'perfil_modelo', 'nombre']  # Sin 'precio'
```

**C. Crear migración:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**D. Actualizar endpoints:**
- Modificar `crear_servicio` para NO aceptar precio
- Modificar `actualizar_servicio` para NO aceptar precio
- Actualizar documentación del API

---

### 3. ✅ ELIMINAR: App de Moderación

#### **Estado Actual:**
La app `moderation` está completamente vacía y no tiene funcionalidad:

```python path=/Users/eduardo/Documents/GitHub/xscort_backend/config/moderation/models.py start=1
from django.db import models
# Create your models here.  ← VACÍO
```

```python path=/Users/eduardo/Documents/GitHub/xscort_backend/config/moderation/views.py start=1
from django.shortcuts import render
# Create your views here.  ← VACÍO
```

#### **Solución Recomendada:**

**A. Eliminar app completamente:**
```bash
# 1. Remover de INSTALLED_APPS
# settings.py línea 51: eliminar 'moderation'

# 2. Eliminar directorio
rm -rf /Users/eduardo/Documents/GitHub/xscort_backend/config/moderation/

# 3. Si hay migraciones, revertirlas primero
python manage.py migrate moderation zero
```

**B. Actualizar settings.py:**
```python
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    # ... otros apps
    'usuarios',
    'perfiles',
    'suscripciones',
    'reviews',
    # 'moderation',  ← ELIMINAR esta línea
]
```

---

### 4. ✅ BUENA IMPLEMENTACIÓN: Sistema de Reseñas

#### **Estado Actual:**
El sistema de reseñas YA está correctamente implementado para usuarios regulares:

**Lo que funciona bien:**

1. **Separación de roles:**
```python path=/Users/eduardo/Documents/GitHub/xscort_backend/config/reviews/views.py start=17
if request.user.es_modelo:
    return Response(
        {"error": "Los modelos no pueden crear reseñas"},
        status=status.HTTP_403_FORBIDDEN
    )
```

2. **Modelo de reseñas:**
```python path=/Users/eduardo/Documents/GitHub/xscort_backend/config/reviews/models.py start=8
class Resena(models.Model):
    perfil_modelo = models.ForeignKey(PerfilModelo, ...)
    cliente = models.ForeignKey(CustomUser, ...)  # ✅ Cualquier usuario
    rating = models.PositiveSmallIntegerField(...)
    comentario = models.TextField()
    aprobada = models.BooleanField(default=False)  # ✅ Moderación
```

3. **Usuarios regulares YA pueden:**
   - Registrarse en el sistema
   - Tener sus propias credenciales
   - Dejar reseñas en perfiles de modelos
   - Las reseñas requieren aprobación (moderación)

**No requiere cambios**, funciona según especificación.

---

### 5. ❌ PROBLEMA CRÍTICO: Endpoint de Subida de Documentos

#### **Análisis del código:**

```python path=/Users/eduardo/Documents/GitHub/xscort_backend/config/usuarios/views.py start=75
class UploadVerificationDocumentsView(APIView):
    """
    Endpoint: POST /api/verification/upload-documents/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Check if user is a modelo
        if not user.es_modelo:  # ❌ PROBLEMA: requiere es_modelo=True
            return Response(
                {"error": "Solo los usuarios modelo pueden subir documentos"},
                status=status.HTTP_403_FORBIDDEN
            )
```

**Problemas identificados:**

1. **Lógica circular:** 
   - Para subir documentos necesitas `es_modelo=True`
   - Para ser modelo necesitas verificación de documentos
   - ¡Paradoja!

2. **Endpoint correcto pero validación incorrecta:**
   - La URL `/api/verification/upload-documents/` es correcta
   - El código de subida de archivos funciona bien
   - El problema es la validación `if not user.es_modelo`

3. **Error esperado en frontend:**
```json
{
  "error": "Solo los usuarios modelo pueden subir documentos"
}
Status: 403 FORBIDDEN
```

#### **Solución Recomendada:**

**A. Eliminar validación incorrecta:**
```python
class UploadVerificationDocumentsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # ❌ ELIMINAR ESTO:
        # if not user.es_modelo:
        #     return Response(...)
        
        # Check if already verified
        if user.esta_verificada:
            return Response(
                {"error": "Tu cuenta ya está verificada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Resto del código está bien...
```

**B. Agregar campo de solicitud de modelo:**
```python
# En usuarios/models.py
class CustomUser(AbstractUser):
    # ... campos existentes
    ha_solicitado_ser_modelo = models.BooleanField(default=False)  # NUEVO
```

**C. Validar que haya solicitado ser modelo:**
```python
def post(self, request):
    user = request.user
    
    # Nueva validación
    if not user.ha_solicitado_ser_modelo:
        return Response(
            {"error": "Primero debes solicitar ser modelo"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if user.esta_verificada:
        return Response(...)
    
    # Procesar documentos...
```

---

## 🎯 RECOMENDACIONES DE ARQUITECTURA

### 1. Estados del Usuario
Implementar un sistema de estados más claro:

```python
class CustomUser(AbstractUser):
    ESTADO_CHOICES = [
        ('REGISTRADO', 'Registrado'),
        ('SOLICITANDO_MODELO', 'Solicitando ser modelo'),
        ('VERIFICANDO', 'En verificación'),
        ('MODELO_ACTIVO', 'Modelo activo'),
        ('CLIENTE', 'Cliente regular'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='REGISTRADO')
```

### 2. Separar Lógica de Verificación
Crear un modelo independiente para solicitudes de verificación:

```python
class SolicitudVerificacion(models.Model):
    usuario = models.ForeignKey(CustomUser, ...)
    foto_documento = models.ImageField(...)
    selfie_con_documento = models.ImageField(...)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    motivo_rechazo = models.TextField(blank=True)
```

### 3. Flujo Completo Propuesto

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO RECOMENDADO PARA MODELOS                              │
└─────────────────────────────────────────────────────────────┘

1. Usuario se registra
   └─ POST /api/register/
   └─ Proporciona: username, email, password, fecha_nacimiento
   └─ Backend valida: edad >= 18 años
   └─ estado = 'REGISTRADO'

2. Usuario solicita ser modelo
   └─ POST /api/request-model-status/
   └─ estado = 'SOLICITANDO_MODELO'
   └─ Ahora puede subir documentos

3. Usuario sube documentos de verificación
   └─ POST /api/verification/upload-documents/
   └─ Adjunta: foto_documento, selfie_con_documento
   └─ Crea SolicitudVerificacion
   └─ estado = 'VERIFICANDO'

4. Admin revisa en panel de administración
   └─ Verifica documentos
   └─ Verifica que coincida con fecha_nacimiento
   └─ Aprueba o rechaza

5. Si se aprueba:
   └─ esta_verificada = True
   └─ es_modelo = True
   └─ estado = 'MODELO_ACTIVO'
   └─ Se crea PerfilModelo automáticamente (signal ya existe)
   └─ Usuario puede completar su perfil público

6. Si se rechaza:
   └─ estado = 'REGISTRADO'
   └─ Puede intentar de nuevo
```

---

## 📝 LISTA DE CAMBIOS NECESARIOS

### Prioridad Alta (Crítico):
- [ ] **Agregar campo `fecha_nacimiento` a CustomUser**
- [ ] **Agregar validación de edad en registro (18+)**
- [ ] **Eliminar o modificar endpoint `become-model`**
- [ ] **Corregir validación en `UploadVerificationDocumentsView`**
- [ ] **Crear modelo `SolicitudVerificacion`**
- [ ] **Eliminar campo `precio` de modelo `Servicio`**

### Prioridad Media:
- [ ] **Eliminar app `moderation` completamente**
- [ ] **Crear nuevo endpoint `request-model-status`**
- [ ] **Agregar campo `estado` a CustomUser**
- [ ] **Actualizar serializers de Servicio**

### Prioridad Baja (Mejoras):
- [ ] **Agregar tests para validación de edad**
- [ ] **Documentar nuevos endpoints en README**
- [ ] **Crear panel de admin personalizado para verificación**

---

## 🔧 COMANDOS PARA APLICAR CAMBIOS

```bash
# 1. Crear migración para nuevos campos
python manage.py makemigrations usuarios

# 2. Crear migración para eliminar precio de servicios
python manage.py makemigrations perfiles

# 3. Aplicar migraciones
python manage.py migrate

# 4. Eliminar app moderation (después de revertir sus migraciones)
python manage.py migrate moderation zero
rm -rf config/moderation/
```

---

## ✅ LO QUE ESTÁ BIEN IMPLEMENTADO

1. **Sistema de autenticación JWT** - Funciona correctamente
2. **Modelo CustomUser** - Buena base, solo falta fecha_nacimiento
3. **Sistema de reseñas** - Correctamente implementado
4. **Separación de perfiles públicos/privados** - Buena arquitectura
5. **Sistema de suscripciones** - Implementado (no analizado en detalle)
6. **Filtros y búsqueda de perfiles** - Bien implementados
7. **Sistema de tags** - Funciona bien
8. **Solicitud de cambio de ciudad** - Buen patrón de aprobación

---

## 🎨 DETALLES FRONTEND (Recomendaciones)

### Login/Registro:
- Usar iconos de **tabler.io** (https://tabler.io/icons)
- Ejemplo: `<IconUser />` para username, `<IconLock />` para password
- Agregar campo de fecha de nacimiento en registro
- Validar edad en frontend Y backend

### Servicios:
- Mostrar solo nombres de servicios (sin precios)
- Eliminar campos de precio de formularios
- UI: Lista simple con nombres

---

## 📞 PRÓXIMOS PASOS SUGERIDOS

1. **Revisar y aprobar este análisis**
2. **Decidir prioridad de implementación**
3. **Crear branch para cambios: `feature/fix-verification-flow`**
4. **Implementar cambios de alta prioridad primero**
5. **Probar flujo completo de registro → verificación → modelo**
6. **Actualizar documentación del API**
7. **Coordinar cambios con frontend**

---

**Fin del Análisis**

¿Necesitas que implemente alguno de estos cambios específicamente?

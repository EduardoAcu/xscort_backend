from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
import logging
from .serializers import UserRegistrationSerializer, UserSerializer, VerificationDocumentsSerializer, UserMeSerializer
from .models import CustomUser, LegalDocument, AgeConsentLog
from .models_password_reset import PasswordResetToken
from perfiles.models import PerfilModelo

logger = logging.getLogger('xscort')


def set_auth_cookies(response, access_token, refresh_token=None):
    """Helper para establecer cookies de autenticación con configuración correcta"""
    # En desarrollo (DEBUG=True), usar secure=False para HTTP
    # En producción (DEBUG=False), usar secure=True para HTTPS
    secure = not settings.DEBUG
    
    # SameSite policy:
    # - En desarrollo (HTTP): usar 'Lax' para permitir cookies cross-site
    # - En producción (HTTPS): usar 'None' (requiere secure=True)
    samesite = 'None' if not settings.DEBUG else 'Lax'
    
    cookie_settings = {
        'httponly': True,
        'path': '/',
        'samesite': samesite,
        'secure': secure,  # Automático: False en dev (HTTP), True en prod (HTTPS)
    }

    # Access token (1 hora)
    response.set_cookie(
        key='access_token',
        value=access_token,
        max_age=3600,
        **cookie_settings
    )

    # Refresh token (1 día) solo si se entrega
    if refresh_token:
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=86400,
            **cookie_settings
        )


class UserRegistrationView(APIView):
    """
    Vista para el registro de nuevos usuarios con cookies HttpOnly.
    Endpoint: POST /api/register/
    
    Al registrarse exitosamente, establece cookies HttpOnly automáticamente.
    """
    permission_classes = [AllowAny]
    # Evita que tokens inválidos en cookies generen 401 antes de llegar a la vista
    authentication_classes = []

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()

            # Registrar versión de términos/privacidad aceptada
            terms_version = request.data.get('terms_version') or None
            privacy_version = request.data.get('privacy_version') or None
            if terms_version or privacy_version:
                user.terms_version = terms_version
                user.privacy_version = privacy_version
                user.save(update_fields=['terms_version', 'privacy_version'])

            # Log de consentimiento de mayoría de edad / legales
            AgeConsentLog.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:1024],
                terms_version=terms_version,
                privacy_version=privacy_version,
            )

            logger.info("Nuevo usuario registrado", extra={
                'username': user.username,
                'email': user.email,
            })

            # Generar tokens JWT para el usuario
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Crear respuesta sin tokens en el body
            response = Response({
                'message': 'Usuario registrado exitosamente',
                'user': UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)
            
            # Establecer cookies HttpOnly
            set_auth_cookies(response, access_token, refresh_token)
            
            return response
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    Vista para el login de usuarios con cookies HttpOnly.
    Endpoint: POST /api/token/
    
    En lugar de retornar tokens en JSON, los establece como cookies HttpOnly.
    """
    permission_classes = [AllowAny]
    # Evita que tokens inválidos en cookies generen 401 antes de llegar a la vista
    authentication_classes = []

    def post(self, request):
        raw_input = request.data.get('username') or request.data.get('email') or ''
        username_input = raw_input.strip()
        password = (request.data.get('password') or '').strip()

        if not username_input or not password:
            return Response({
                'error': 'Por favor proporcione username y password'
            }, status=status.HTTP_400_BAD_REQUEST)
        # Permitir login con email o username
        user = None
        if "@" in username_input:
            username_input = username_input.lower()
            try:
                user_obj = CustomUser.objects.get(email=username_input)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                user = None
        if user is None:
            user = authenticate(username=username_input.lower(), password=password)

        if user is not None:
            logger.info("Login exitoso", extra={'username': user.username})
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            logger.info(f"Tokens generados - Access: {access_token[:20]}... Refresh: {refresh_token[:20]}...")
            
            # Crear respuesta sin tokens en el body
            response = Response({
                'message': 'Login exitoso',
                'user': UserSerializer(user).data,
            }, status=status.HTTP_200_OK)
            
            # Establecer cookies HttpOnly
            set_auth_cookies(response, access_token, refresh_token)
            logger.info(f"Cookies establecidas - secure={not settings.DEBUG}")
            
            return response
        
        logger.warning("Login fallido", extra={'username': username_input})

        return Response({
            'error': 'Credenciales inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    """
    Vista para logout de usuarios (limpia cookies HttpOnly).
    Endpoint: POST /api/logout/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({
            'message': 'Logout exitoso'
        }, status=status.HTTP_200_OK)
        
        # Eliminar cookies estableciendo max_age=0
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        
        logger.info("Logout exitoso", extra={'username': request.user.username})
        
        return response


class UploadVerificationDocumentsView(APIView):
    """
    Vista para subir documentos de verificación.
    Endpoint: POST /api/verification/upload-documents/
    
    Requiere autenticación y que el usuario haya solicitado ser modelo.
    Body esperado (multipart/form-data):
    - foto_documento: archivo de imagen (opcional si se envía selfie_con_documento)
    - selfie_con_documento: archivo de imagen (opcional si se envía foto_documento)
    
    Al menos uno de los dos campos debe estar presente.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        ciudad_id = request.data.get('ciudad_id')
        if not ciudad_id:
            return Response(
                {"error": "Debe seleccionar una ciudad (ciudad_id) para solicitar ser modelo"},
                status=status.HTTP_400_BAD_REQUEST
            )
        from perfiles.models import Ciudad, PerfilModelo
        try:
            ciudad = Ciudad.objects.get(id=ciudad_id)
        except Ciudad.DoesNotExist:
            return Response({"error": "Ciudad no válida"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has requested to be a model
        if not user.ha_solicitado_ser_modelo:
            return Response(
                {"error": "Primero debes solicitar ser modelo. Usa el endpoint /api/request-model-verification/"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already verified
        if user.esta_verificada:
            return Response(
                {"error": "Tu cuenta ya está verificada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare data with files
        data = {}
        if 'foto_documento' in request.FILES:
            data['foto_documento'] = request.FILES['foto_documento']
        if 'selfie_con_documento' in request.FILES:
            data['selfie_con_documento'] = request.FILES['selfie_con_documento']
        
        serializer = VerificationDocumentsSerializer(user, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            logger.info("Documentos de verificación subidos", extra={'user_id': user.id, 'username': user.username})
            return Response(
                {
                    "message": "Documentos subidos exitosamente. Tu cuenta será revisada por un administrador.",
                    "data": {
                        "foto_documento": serializer.data.get('foto_documento'),
                        "selfie_con_documento": serializer.data.get('selfie_con_documento'),
                    }
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerificationStatusView(APIView):
    """Devuelve el estado de verificación del usuario autenticado.

    Endpoint: GET /api/verification/status/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tiene_documentos = bool(user.foto_documento or user.selfie_con_documento)

        data = {
            "esta_verificada": bool(user.esta_verificada),
            "tiene_documentos": tiene_documentos,
            "es_modelo": bool(user.es_modelo),
            "username": user.username,
            "email": user.email,
        }

        return Response(data, status=status.HTTP_200_OK)


class UserMeView(APIView):
    """Permite al usuario autenticado ver/actualizar su perfil básico."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserMeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LatestTermsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        doc = LegalDocument.objects.filter(tipo='terms', is_current=True).first()
        if not doc:
            return Response({"error": "Términos no configurados"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"version": doc.version, "body": doc.body}, status=status.HTTP_200_OK)


class LatestPrivacyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        doc = LegalDocument.objects.filter(tipo='privacy', is_current=True).first()
        if not doc:
            return Response({"error": "Política no configurada"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"version": doc.version, "body": doc.body}, status=status.HTTP_200_OK)


class RequestModelVerificationView(APIView):
    """
    Solicita verificación para ser modelo.
    Endpoint: POST /api/request-model-verification/
    
    Este endpoint marca al usuario como solicitante de modelo,
    permitiendo subir documentos de verificación.
    El usuario NO será modelo hasta que un admin apruebe los documentos.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        logger.info(f"RequestModelVerificationView - User: {user}, Authenticated: {user.is_authenticated}, Cookies: {request.COOKIES}")
        
        ciudad_id = request.data.get('ciudad_id')
        
        # Validar que se proporcionó ciudad_id
        if not ciudad_id:
            return Response(
                {"error": "Debe seleccionar una ciudad (ciudad_id) para solicitar ser modelo"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Importar Ciudad para validar
        from perfiles.models import Ciudad
        try:
            ciudad = Ciudad.objects.get(id=ciudad_id)
        except Ciudad.DoesNotExist:
            return Response({"error": "Ciudad no válida"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya es modelo verificado
        if user.es_modelo and user.esta_verificada:
            return Response(
                {"message": "Ya eres un modelo verificado"},
                status=status.HTTP_200_OK
            )
        
        # Verificar si ya solicitó
        if user.ha_solicitado_ser_modelo:
            return Response(
                {
                    "message": "Ya has solicitado ser modelo. Ahora puedes subir tus documentos de verificación.",
                    "next_step": "POST /api/verification/upload-documents/"
                },
                status=status.HTTP_200_OK
            )
        
        # Marcar como solicitante
        user.ha_solicitado_ser_modelo = True
        # Marcar como modelo y asegurar PerfilModelo
        user.es_modelo = True
        user.save(update_fields=['ha_solicitado_ser_modelo', 'es_modelo'])

        # Crear perfil de modelo si no existe, con ciudad requerida
        perfil, _ = PerfilModelo.objects.get_or_create(user=user, defaults={'ciudad': ciudad})
        if perfil.ciudad_id != ciudad.id:
            perfil.ciudad = ciudad
            perfil.save(update_fields=['ciudad'])
        
        return Response(
            {
                "message": "Solicitud registrada. Ahora debes subir tus documentos de verificación.",
                "next_step": "POST /api/verification/upload-documents/",
                "required_documents": ["foto_documento", "selfie_con_documento"]
            },
            status=status.HTTP_200_OK
        )


class ForgotPasswordView(APIView):
    """
    Solicita recuperación de contraseña.
    Endpoint: POST /api/auth/forgot-password/
    
    Body: { "email": "usuario@example.com" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Invalidar tokens anteriores del mismo usuario
            PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
            
            # Crear nuevo token
            reset_token = PasswordResetToken.objects.create_token(user)
            
            # Construir URL de reset
            frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
            reset_url = f"{frontend_url}/reset-password/{reset_token.token}"
            
            # Enviar email
            subject = 'Recuperación de Contraseña - xscort.cl'
            message = f"""
Hola {user.username},

Has solicitado recuperar tu contraseña en xscort.cl.

Para crear una nueva contraseña, haz clic en el siguiente enlace:
{reset_url}

Este enlace expirará en 1 hora.

Si no solicitaste este cambio, puedes ignorar este correo.

Saludos,
Equipo de xscort.cl
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Email de recuperación enviado a {user.email}")
            except Exception as e:
                logger.error(f"Error enviando email: {e}")
                # No revelamos si el email existe o no por seguridad
            
            # Siempre retornar el mismo mensaje (no revelar si el usuario existe)
            return Response({
                'message': 'Si el email existe, recibirás un correo con instrucciones para recuperar tu contraseña.'
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            # Por seguridad, no revelar que el usuario no existe
            return Response({
                'message': 'Si el email existe, recibirás un correo con instrucciones para recuperar tu contraseña.'
            }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    Establece nueva contraseña usando token.
    Endpoint: POST /api/auth/reset-password/
    
    Body: { 
        "token": "...",
        "new_password": "...",
        "confirm_password": "..."
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token_str = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validaciones
        if not token_str or not new_password or not confirm_password:
            return Response({
                'error': 'Token, nueva contraseña y confirmación son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'error': 'Las contraseñas no coinciden'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({
                'error': 'La contraseña debe tener al menos 8 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar token
        try:
            reset_token = PasswordResetToken.objects.get(token=token_str)
            
            if not reset_token.is_valid():
                return Response({
                    'error': 'El token ha expirado o ya fue usado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Cambiar contraseña
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Marcar token como usado
            reset_token.mark_as_used()
            
            logger.info(f"Contraseña cambiada exitosamente para {user.username}")
            
            return Response({
                'message': 'Contraseña cambiada exitosamente. Ya puedes iniciar sesión.'
            }, status=status.HTTP_200_OK)
            
        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': 'Token inválido'
            }, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshCookieView(APIView):
    """
    Refresca el access_token leyendo refresh_token desde cookie HttpOnly.
    Endpoint: POST /api/token/refresh/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'No hay refresh_token'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            response = Response({'message': 'Token refrescado'}, status=status.HTTP_200_OK)
            set_auth_cookies(response, access_token, None)
            return response
        except Exception:
            return Response({'error': 'Refresh token inválido o expirado'}, status=status.HTTP_401_UNAUTHORIZED)

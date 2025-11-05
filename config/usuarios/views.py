from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserSerializer, VerificationDocumentsSerializer


class UserRegistrationView(APIView):
    """
    Vista para el registro de nuevos usuarios.
    Endpoint: POST /api/register/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generar tokens JWT para el usuario
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    Vista para el login de usuarios.
    Endpoint: POST /api/token/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': 'Por favor proporcione username y password'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Autenticar usuario
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login exitoso',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Credenciales inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)


class UploadVerificationDocumentsView(APIView):
    """
    Vista para subir documentos de verificación.
    Endpoint: POST /api/verification/upload-documents/
    
    Requiere autenticación.
    Body esperado (multipart/form-data):
    - foto_documento: archivo de imagen (opcional si se envía selfie_con_documento)
    - selfie_con_documento: archivo de imagen (opcional si se envía foto_documento)
    
    Al menos uno de los dos campos debe estar presente.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Check if user is a modelo
        if not user.es_modelo:
            return Response(
                {"error": "Solo los usuarios modelo pueden subir documentos de verificación"},
                status=status.HTTP_403_FORBIDDEN
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

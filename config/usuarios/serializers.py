from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de nuevos usuarios.
    Requiere fecha de nacimiento y valida mayoría de edad (18+).
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirmar contraseña'
    )

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'password',
            'password2',
            'fecha_nacimiento',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'fecha_nacimiento': {'required': True},
        }

    def validate(self, attrs):
        """
        Validar que ambas contraseñas coincidan y que el usuario sea mayor de edad.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })
        
        # Validar mayoría de edad (18 años)
        fecha_nacimiento = attrs.get('fecha_nacimiento')
        if fecha_nacimiento:
            hoy = date.today()
            edad = relativedelta(hoy, fecha_nacimiento).years
            
            if edad < 18:
                raise serializers.ValidationError({
                    "fecha_nacimiento": "Debes ser mayor de 18 años para registrarte."
                })
        
        return attrs

    def create(self, validated_data):
        """
        Crear nuevo usuario con contraseña encriptada.
        """
        # Remover password2 ya que no es parte del modelo
        validated_data.pop('password2')
        
        # Crear usuario con create_user para hashear la contraseña correctamente
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            fecha_nacimiento=validated_data.get('fecha_nacimiento'),
        )
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar y actualizar el perfil de usuario.
    """
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'esta_verificada',
        ]
        read_only_fields = [
            'id',
            'esta_verificada',
        ]


class VerificationDocumentsSerializer(serializers.ModelSerializer):
    """
    Serializer para subir documentos de verificación.
    """
    class Meta:
        model = CustomUser
        fields = [
            'foto_documento',
            'selfie_con_documento',
        ]
    
    def validate(self, attrs):
        """
        Validar que al menos uno de los documentos esté presente.
        """
        if not attrs.get('foto_documento') and not attrs.get('selfie_con_documento'):
            raise serializers.ValidationError(
                "Debes subir al menos un documento (foto_documento o selfie_con_documento)"
            )
        return attrs

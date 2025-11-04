from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de nuevos usuarios.
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
        ]
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, attrs):
        """
        Validar que ambas contraseñas coincidan.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
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

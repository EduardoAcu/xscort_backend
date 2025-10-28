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
            'nombre_fantasia',
            'genero',
            'edad',
            'telefono',
            'ciudad',
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
            nombre_fantasia=validated_data.get('nombre_fantasia', ''),
            genero=validated_data.get('genero', ''),
            edad=validated_data.get('edad'),
            telefono=validated_data.get('telefono', ''),
            ciudad=validated_data.get('ciudad', ''),
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
            'nombre_fantasia',
            'genero',
            'edad',
            'medidas',
            'peso',
            'altura',
            'ciudad',
            'telefono',
            'biografia',
            'esta_verificada',
            'email_verified',
            'phone_verified',
            'identity_verified',
            'verification_status',
        ]
        read_only_fields = [
            'id',
            'esta_verificada',
            'email_verified',
            'phone_verified',
            'identity_verified',
            'verification_status',
        ]

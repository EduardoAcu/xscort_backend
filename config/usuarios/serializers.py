from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import CustomUser


class UsernameCheckSerializer(serializers.Serializer):
    """
    Serializador para validar si un nombre de usuario está disponible.
    """
    username = serializers.CharField(
        max_length=150,
        required=True,
        allow_blank=False,
        trim_whitespace=True
    )
    
    def validate_username(self, value):
        """
        Validar que el username tenga un formato válido.
        Django por defecto permite: letras, dígitos y @/./+/-/_
        """
        # Convertir a slug para validación básica
        slug_value = slugify(value)
        if not slug_value:
            raise serializers.ValidationError(
                "El nombre de usuario debe contener al menos un carácter válido (letras o números)"
            )
        if len(value) < 3:
            raise serializers.ValidationError(
                "El nombre de usuario debe tener al menos 3 caracteres"
            )
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro.
    El username es OBLIGATORIO y debe ser único.
    """
    # 1. CAMBIO CLAVE: required=True y validamos longitud mínima
    username = serializers.CharField(
        required=True, 
        min_length=3,
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
            'blank': 'El nombre de usuario no puede estar vacío.'
        }
    )
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

    def validate_username(self, value):
        """
        Valida que el usuario sea único y tenga formato válido.
        NO genera nombres automáticos.
        """
        # Convertir a formato URL-friendly (ej: "María 69" -> "maria-69")
        slug_value = slugify(value)
        
        if not slug_value:
            raise serializers.ValidationError("El nombre de usuario contiene caracteres no válidos.")

        # Verificar duplicados exactos en la BD
        if CustomUser.objects.filter(username__iexact=slug_value).exists():
            raise serializers.ValidationError()
        
        # Retornamos el valor limpio (slugified) para que se guarde así
        return slug_value

    def validate(self, attrs):
        # 1. Validar contraseñas
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })
        
        # 2. Validar email único
        email = (attrs.get('email') or '').strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({
                "email": "Este correo electrónico ya está registrado."
            })
        attrs['email'] = email
        
        # 3. Validar mayoría de edad
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
        Crea el usuario con los datos ya validados y limpios.
        """
        validated_data.pop('password2')

        username = validated_data['username'] # Ya viene limpio del validate_username
        email = validated_data['email']
        
        # Opcional: intentar sacar primer nombre del username
        parts = username.split('-')
        first_name = parts[0] if parts else ''
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            fecha_nacimiento=validated_data.get('fecha_nacimiento'),
            first_name=first_name,
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
            'es_modelo',
        ]
        read_only_fields = [
            'id',
            'esta_verificada',
            'es_modelo',
        ]


class UserMeSerializer(serializers.ModelSerializer):
    """Serializer para que el usuario actual edite datos básicos."""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']

    def validate_username(self, value):
        # Evitar duplicados
        qs = CustomUser.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ese nombre de usuario ya está en uso")
        return value

    def validate_email(self, value):
        qs = CustomUser.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ese correo ya está en uso")
        return value


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

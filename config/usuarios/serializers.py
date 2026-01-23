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
    Serializer para el registro de nuevos usuarios.
    Requiere fecha de nacimiento y valida mayoría de edad (18+).
    """
    # Permitimos que el usuario escriba nombre completo; no aplicamos el validador regex por defecto.
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True, validators=[])
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
        
        # Generar username seguro ANTES de validaciones de modelo
        raw_name = (attrs.get('username') or '').strip()
        email = (attrs.get('email') or '').strip().lower()
        attrs['email'] = email
        attrs['username'] = self._build_username(raw_name, email)
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

    def _build_username(self, raw_name, email):
        """
        Genera un username seguro y único a partir del nombre ingresado o el email.
        Permite que el usuario escriba nombre completo; se transforma a slug.
        """
        base = slugify(raw_name) or slugify(email.split("@")[0])
        base = base or "user"
        candidate = base
        counter = 1
        while CustomUser.objects.filter(username=candidate).exists():
            candidate = f"{base}-{counter}"
            counter += 1
        return candidate

    def create(self, validated_data):
        """
        Crear nuevo usuario con contraseña encriptada.
        """
        # Remover password2 ya que no es parte del modelo
        validated_data.pop('password2')

        full_name = validated_data.get('username', '') or ''
        email = validated_data['email']
        username_safe = self._build_username(full_name, email)

        # Intentar separar nombre y apellido (opcional)
        parts = full_name.strip().split()
        first_name = parts[0] if parts else ''
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        
        # Crear usuario con create_user para hashear la contraseña correctamente
        user = CustomUser.objects.create_user(
            username=username_safe,
            email=email,
            password=validated_data['password'],
            fecha_nacimiento=validated_data.get('fecha_nacimiento'),
            first_name=first_name,
            last_name=last_name,
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

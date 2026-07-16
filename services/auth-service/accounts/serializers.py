from rest_framework import serializers
from .models import AuditoriaAcceso, Cliente, Direccion, Usuario


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    contrasena = serializers.CharField(write_only=True)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "correo", "rol", "estado_cuenta", "creado_en"]
        read_only_fields = ["id", "rol", "creado_en"]


class UsuarioCrearSerializer(serializers.ModelSerializer):
    contrasena = serializers.CharField(write_only=True, min_length=8, source="password")

    class Meta:
        model = Usuario
        fields = ["id", "correo", "contrasena", "rol", "estado_cuenta", "creado_en"]
        read_only_fields = ["id", "rol", "estado_cuenta", "creado_en"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class UsuarioActualizarSerializer(serializers.ModelSerializer):
    contrasena = serializers.CharField(write_only=True, required=False, min_length=8, source="password")

    class Meta:
        model = Usuario
        fields = ["correo", "contrasena", "rol", "estado_cuenta"]


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "usuario", "nombre_completo", "telefono", "idioma_preferido", "puntos_lealtad"]
        read_only_fields = ["id", "usuario"]


class ClienteCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["nombre_completo", "telefono", "idioma_preferido", "puntos_lealtad"]


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ["id", "cliente", "calle", "numero_exterior", "colonia", "ciudad",
                  "estado_provincia", "codigo_postal", "pais", "es_principal"]
        read_only_fields = ["id", "cliente"]


class DireccionCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ["cliente", "calle", "numero_exterior", "colonia", "ciudad",
                  "estado_provincia", "codigo_postal", "pais", "es_principal"]
        extra_kwargs = {"cliente": {"required": False}}


class AuditoriaAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditoriaAcceso
        fields = ["id", "usuario", "correo_intentado", "ip", "user_agent", "exitoso", "creado_en"]

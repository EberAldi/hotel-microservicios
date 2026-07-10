import bcrypt
from rest_framework import serializers

from .models import Usuario, Cliente


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer de Usuario para CRUD completo.
    - 'contrasena' es write_only. Requerido al crear (POST).
    - Opcional al actualizar (PUT/PATCH): si no se manda, se conserva el hash actual.
    - 'contrasena_hash' nunca se expone en la respuesta.
    """
    contrasena = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = Usuario
        fields = ['id', 'correo', 'contrasena', 'rol', 'estado_cuenta', 'creado_en']
        read_only_fields = ['id', 'creado_en']

    def create(self, validated_data):
        contrasena_plana = validated_data.pop('contrasena', None)

        if not contrasena_plana:
            raise serializers.ValidationError(
                {'contrasena': 'Este campo es requerido al crear un usuario.'}
            )

        validated_data['contrasena_hash'] = self._hash(contrasena_plana)
        return Usuario.objects.create(**validated_data)

    def update(self, instance, validated_data):
        contrasena_plana = validated_data.pop('contrasena', None)

        if contrasena_plana:
            instance.contrasena_hash = self._hash(contrasena_plana)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    @staticmethod
    def _hash(contrasena_plana):
        return bcrypt.hashpw(
            contrasena_plana.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')


class ClienteSerializer(serializers.ModelSerializer):
    """
    Perfil de cliente.
    El campo 'usuario' se obtiene automáticamente desde el JWT
    en ClienteViewSet.perform_create().
    """

    class Meta:
        model = Cliente
        fields = [
            'id',
            'usuario',
            'nombre_completo',
            'telefono',
            'idioma_preferido',
            'puntos_lealtad'
        ]
        read_only_fields = ['id', 'usuario']
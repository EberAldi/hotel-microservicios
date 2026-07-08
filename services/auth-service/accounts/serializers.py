import bcrypt
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer basico de User, sin JWT todavia.
    - 'password' es write_only: entra en texto plano, nunca se devuelve.
    - 'password_hash' nunca se expone en la respuesta.
    - El hash se genera con bcrypt antes de guardar (requerimiento del proyecto).
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'role', 'account_status', 'created_at']
        read_only_fields = ['id', 'account_status', 'created_at']

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        password_hash = bcrypt.hashpw(
            raw_password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')
        return User.objects.create(password_hash=password_hash, **validated_data)
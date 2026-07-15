from rest_framework import serializers
from .models import TipoHabitacion, Habitacion, ImagenHabitacion, DisponibilidadHabitacion


class TipoHabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoHabitacion
        fields = ['id', 'nombre', 'descripcion', 'capacidad_maxima']
        read_only_fields = ['id']


class ImagenHabitacionSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ImagenHabitacion
        fields = ['id', 'habitacion', 'imagen', 'imagen_url', 'orden', 'es_principal', 'alt_text']
        read_only_fields = ['id', 'imagen_url']
        extra_kwargs = {'imagen': {'write_only': True}}

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class HabitacionSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)

    class Meta:
        model = Habitacion
        fields = ['id', 'numero', 'tipo', 'tipo_nombre', 'precio_base', 'estado']
        read_only_fields = ['id']


class DisponibilidadHabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisponibilidadHabitacion
        fields = ['id', 'habitacion', 'fecha', 'estado']
        read_only_fields = ['id']
from rest_framework import serializers
from .models import CategoriaServicio, Servicio, ImagenServicio


class CategoriaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaServicio
        fields = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']


class ImagenServicioSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ImagenServicio
        fields = ['id', 'servicio', 'imagen', 'imagen_url', 'orden', 'es_principal', 'alt_text']
        read_only_fields = ['id', 'imagen_url']
        extra_kwargs = {'imagen': {'write_only': True}}

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class ServicioSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'categoria', 'categoria_nombre', 'precio']
        read_only_fields = ['id']
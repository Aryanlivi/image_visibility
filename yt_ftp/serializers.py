from rest_framework import serializers
from .models import URL, ImageMetadata

# Serializer for ImageMetadata model
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMetadata
        fields = ['device_id', 'devicecode', 'album_code', 'latitude', 'longitude', 'altitude', 'imageowner', 'angle']

# Serializer for URL model
class URLSerializer(serializers.ModelSerializer):
    # Nested ImageMetadata serializer
    image_metadata = ImageSerializer()

    class Meta:
        model = URL
        fields = ['url', 'name', 'status', 'capture_interval', 'last_run', 'created_at', 'updated_at','image_metadata']

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
        fields = ['id','url', 'name', 'capture_interval', 'image_metadata']
    
    def create(self, validated_data):
        # Extract image_metadata from validated_data
        image_metadata_data = validated_data.pop('image_metadata')
        # Create URL instance
        url_instance = URL.objects.create(**validated_data)
        
        # Create ImageMetadata instance related to the URL
        ImageMetadata.objects.create(
            url=url_instance, 
            **image_metadata_data  
        )

        return url_instance

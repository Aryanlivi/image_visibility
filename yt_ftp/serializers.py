from rest_framework import serializers
from .models import URL, ImageMetadata

# Serializer for ImageMetadata model
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMetadata
        fields = ['id','device_id', 'devicecode', 'album_code', 'latitude', 'longitude', 'altitude', 'imageowner', 'angle']

# Serializer for URL model
class URLSerializer(serializers.ModelSerializer):
    # Nested ImageMetadata serializer
    image_metadata = ImageSerializer()
    class Meta:
        model = URL
        fields = ['id','url','name','active','capture_interval', 'image_metadata']
        read_only_fields=['active']
    
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
    
    def update(self, instance, validated_data):
        # Extract and update nested image_metadata
        image_metadata_data = validated_data.pop('image_metadata', None)

        # Update the URL instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  

        # If image_metadata is present, update or create the related instance
        if image_metadata_data:
            image_metadata_instance = instance.image_metadata  # Related `ImageMetadata` instance
            for attr, value in image_metadata_data.items():
                setattr(image_metadata_instance, attr, value)
            image_metadata_instance.save()

        return instance 

from rest_framework import serializers
from .models import URL, ImageMetadata,CustomPeriodicTask,FTPConfig
from django.db import transaction
from django.db.models.signals import post_save
from yt_ftp.signals.handlers import start_celery_task


# Serializer for ImageMetadata model
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMetadata
        fields = ['id','device_id', 'devicecode', 'album_code', 'latitude', 'longitude', 'altitude', 'imageowner', 'angle']
class SimpleFTPConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = FTPConfig
        fields = ['id','ftp_server','remote_directory']
class FTPConfigSerializer(serializers.ModelSerializer):
    ftp_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = FTPConfig 
        fields = ['id', 'ftp_server', 'ftp_username', 'ftp_password', 'remote_directory', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        ftp_password = validated_data.pop('ftp_password')
        ftp_config = FTPConfig(**validated_data)
        ftp_config.set_password(ftp_password)
        ftp_config.save()
        return ftp_config

    def update(self, instance, validated_data):
        if 'ftp_password' in validated_data:
            ftp_password = validated_data.pop('ftp_password')
            instance.set_password(ftp_password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

# Serializer for URL model   
class URLSerializer(serializers.ModelSerializer):
    # Nested ImageMetadata serializer
    image_metadata = ImageSerializer()
    ftp_configs = serializers.ListField(write_only=True) # accept only list of ftp_configs ids
    last_run_at=serializers.SerializerMethodField()
    class Meta:
        model = URL
        fields = ['id','url','name','active','capture_interval', 'image_metadata','last_run_at','ftp_configs']
    
    def get_last_run_at(self, obj):
        task = obj.customperiodictask_set.first()  # Get the first related task
        if task:
            return task.last_run_at
        return None  # Or return a default value if no task exists
    
    def to_representation(self, instance):
        """Modify the representation to return full FTPConfig details."""
        representation = super().to_representation(instance)
        representation['ftp_configs'] = SimpleFTPConfigSerializer(instance.ftp_configs.all(), many=True).data
        return representation
    def create(self, validated_data):
        # Temporarily disconnect the post_save signal for the URL model
        post_save.disconnect(start_celery_task, sender=URL)
        
        url_instance = None
        try:
            with transaction.atomic():
                # Extract image_metadata from validated_data
                image_metadata_data = validated_data.pop('image_metadata')
                ftp_ids = validated_data.pop('ftp_configs')  # This is a list of integers
                
                # Create URL instance first
                url_instance = URL.objects.create(**validated_data)
                
                # Fetch and associate FTPConfigs using IDs
                ftp_configs = FTPConfig.objects.filter(id__in=ftp_ids)  # Fetch by IDs
                url_instance.ftp_configs.set(ftp_configs)  # Assign many-to-many

                # Reconnect the post_save signal for the URL model before saving image_metadata
                post_save.connect(start_celery_task, sender=URL)

                # Create ImageMetadata instance related to the URL
                image_metadata_instance = ImageMetadata.objects.create(
                    url=url_instance,
                    **image_metadata_data
                )

        except Exception as e:
            # Handle any exceptions here (e.g., rollback transaction if needed)
            if url_instance:
                url_instance.delete()  # Rollback the created URL if there is any error
            raise e

        return url_instance
    
    def update(self, instance, validated_data):
        with transaction.atomic():
            image_metadata_data = validated_data.pop('image_metadata', None)

            #USING URL_UPDATED TO CALL SAVE METHOD EVEN FOR CHANGES IN IMAGE METADATA.

            # Track whether the URL instance is updated
            url_updated = False  

            # Update the URL instance fields
            for attr, value in validated_data.items():
                if getattr(instance, attr) != value:  # Only update if changed
                    setattr(instance, attr, value)
                    url_updated = True  

            if url_updated:  
                instance.save()  # Only save if actual changes happened  

            # If image_metadata is present, update or create the related instance
            if image_metadata_data:
                image_metadata_instance = instance.image_metadata
                metadata_updated = False  

                for attr, value in image_metadata_data.items():
                    if getattr(image_metadata_instance, attr) != value:  # Check if values changed
                        setattr(image_metadata_instance, attr, value)
                        metadata_updated = True  

                if metadata_updated:
                    image_metadata_instance.save()
                    instance.save()  # Save URL again to trigger post_save

            return instance


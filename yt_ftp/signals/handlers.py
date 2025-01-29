from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from yt_ftp.models import URL,ImageMetadata
from yt_ftp.tasks import process_all_urls
@receiver(post_save, sender=URL)
def start_celery_task(sender, instance, **kwargs):
    instance.refresh_from_db()  # This reloads the instance and its relations
    first_angle, last_angle = str(instance.image_metadata.angle).split(".")
    CONSTANTS = {
            "device_id": instance.image_metadata.device_id,  # pick a random id
            "devicecode": instance.image_metadata.devicecode,    
            "album_code": instance.image_metadata.album_code,
            "latitude": instance.image_metadata.latitude,
            "longitude": instance.image_metadata.longitude,
            "altitude": instance.image_metadata.altitude,
            "imageowner": instance.image_metadata.imageowner,
            "firstAngle": int(first_angle),
            "lastAngle":int(last_angle),
        }
    process_all_urls(CONSTANTS)  # Pass the dictionary as a parameter
    print("POST SAVE CALLED!")


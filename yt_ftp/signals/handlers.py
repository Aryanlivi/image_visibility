from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from yt_ftp.models import URL,ImageMetadata
from yt_ftp.tasks import process_all_urls
from django.db import transaction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# This is your receiver method
@receiver(post_save, sender=URL)
@receiver(post_save, sender=ImageMetadata)
def start_celery_task(sender, instance, created, **kwargs):
    print(f"Signal triggered for URL: {instance}, created: {created}")
    if created:  # Only trigger the task if it's a new object
        if sender==URL:
            # We need to ensure that the related image_metadata is saved and available
            run_celery_task(instance.image_metadata)
        if sender==ImageMetadata:
            run_celery_task(instance)
            

        

def run_celery_task(instance):
    print("RAN CELERY TASK")
    try:
        # # Refresh instance after commit
        # instance.refresh_from_db()
        # first_angle, last_angle = str(instance.angle).split(".")
        
        # CONSTANTS = {
        #     "device_id": instance.device_id,  # pick a random id
        #     "devicecode": instance.devicecode,
        #     "album_code": instance.album_code,
        #     "latitude": instance.latitude,
        #     "longitude": instance.longitude,
        #     "altitude": instance.altitude,
        #     "imageowner": instance.imageowner,
        #     "firstAngle": int(first_angle),
        #     "lastAngle": int(last_angle),
        # }
        
        # Delay ensures async call
        process_all_urls.apply_async()
    except Exception as e:
        logger.error(f"Error in start_celery_task for {instance}: {e}")
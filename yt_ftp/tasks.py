from celery import shared_task
from .models import URL,ImageMetadata,CustomPeriodicTask
import logging
from .YoutubeHandler import YoutubeHandler
from .ImageHandler import ImageHandler
from django.utils.timezone import now
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_url(self,url_instance_id,ftp_configs=None):
    """        
    Celery task to process  URL and take screenshots.
    """
    try:
        url_instance = URL.objects.get(id=url_instance_id)
        
        # Get FTP configurations for the URL that doesnt trigger signal and is already active
        if ftp_configs is None:
            ftp_configs=URL.objects.get_ftp_configs_for_url(url_instance)
            
        task = CustomPeriodicTask.objects.get(url_instance=url_instance)
        if not task.enabled:
            logger.warning(f"{task} Not enabled")
            return
        metadata=ImageMetadata.objects.filter(url=url_instance).first()
        logger.debug(f"Processing URL: {url_instance}")
        BASE_OUTPUT_DIR = f"./screenshots/{url_instance.name}"
        yt_handler = YoutubeHandler(url_instance.url, BASE_OUTPUT_DIR)
        img_path, capture_time = yt_handler.capture_screenshot()
        logger.debug(f"capture:{capture_time}")
        img_handler = ImageHandler(img_path)
        maker_note = img_handler.create_encoded_maker_note(
            device_id=metadata.device_id,
            devicecode=metadata.devicecode,    
            album_code=metadata.album_code,
            latitude=metadata.latitude,
            longitude=metadata.longitude,
            altitude=metadata.altitude,
            imageowner=metadata.imageowner,
            datetime_taken=capture_time,  # Assuming capture_time exists in ImageMetadata
        )
        
        first_angle, last_angle = str(metadata.angle).split(".")
        file_name = img_handler.add_metadata_and_save(
            maker_note,
            firstangle=int(first_angle),  # Assuming these fields exist in ImageMetadata
            lastangle=int(last_angle),
        ) 
        
        img_handler.test_upload_ftp(ftp_configs)
        # Uncomment this to upload the file to FTP
        # img_handler.upload_to_ftp(file_to_upload=file_name)

        logger.info(f"Successfully processed URL: {url_instance.name}")
        # # Update last_run_at timestamp 
        try:
            task.last_run_at = now()
            task.save()
        except CustomPeriodicTask.DoesNotExist:
            logger.warning(f"Task {self.name} not found in PeriodicTask table") 
    except Exception as e:
        logger.error(f"-------Error processing URL: {e}")


from celery import shared_task
from .models import URL,ImageMetadata
import logging
from .YoutubeHandler import YoutubeHandler
from .ImageHandler import ImageHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_url(self,url_instance_id):
    """        
    Celery task to process  URL and take screenshots.
    """
    try:
        url_instance = URL.objects.get(id=url_instance_id)
        metadata=ImageMetadata.objects.filter(url=url_instance).first()
        logger.info(f"Processing URL: {url_instance}")
        BASE_OUTPUT_DIR = f"./screenshots/{url_instance.name}"
        yt_handler = YoutubeHandler(url_instance.url, BASE_OUTPUT_DIR)
        img_path, capture_time = yt_handler.capture_screenshot()

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

        # # Uncomment this to upload the file to FTP
        # # img_handler.upload_to_ftp(file_to_upload=file_name)

        logger.info(f"Successfully processed URL: {url_instance.url}")
    except Exception as e:
        logger.error(f"-------Error processing URL: {e}")


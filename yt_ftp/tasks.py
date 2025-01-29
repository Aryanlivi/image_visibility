from .utils import wait_for_next_10_minute_interval
from .models import URL
import logging
import time
from .YoutubeHandler import YoutubeHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# @shared_task(bind=True)
def process_all_urls(CONSTANTS):
    """
    Celery task to process all URLs from Redis and take screenshots every 10 minutes.
    """
    try:
        while True:
            # Wait for the next 10-minute interval to always start capturing from the 10 min interval gap
            # wait_for_next_10_minute_interval()
            urls=URL.objects.filter(active=True).all()
            
            # Process each stream
            for url_instance in urls:
                try:
                    logger.info(f"Processing URL: {url_instance}")
                    BASE_OUTPUT_DIR = f"./screenshots/"+url_instance.name
                    yt_handler = YoutubeHandler(url_instance.url, BASE_OUTPUT_DIR)            
                    img_path, capture_time = yt_handler.capture_screenshot() 
                    img_handler = ImageHandler(img_path)
                    maker_note = img_handler.create_encoded_maker_note(
                        device_id=CONSTANTS["device_id"],
                        devicecode=CONSTANTS["devicecode"],
                        album_code=CONSTANTS["album_code"],
                        latitude=CONSTANTS["latitude"],
                        longitude=CONSTANTS["longitude"],
                        altitude=CONSTANTS["altitude"],
                        imageowner=CONSTANTS["imageowner"],
                        datetime_taken=capture_time,
                    )

                    # Add metadata and upload to FTP
                    file_name = img_handler.add_metadata_and_save(
                        maker_note,
                        firstangle=CONSTANTS["firstAngle"],
                        lastangle=CONSTANTS["lastAngle"],
                    )
                    # img_handler.upload_to_ftp(file_to_upload=file_name)
                    logger.info(f"BASE:{BASE_OUTPUT_DIR}")
                    logger.info(f"Successfully processed URL: {url_instance.url}")
                except Exception as e:
                    logger.error(f"Error processing URL {url_instance}: {e}")
            time.sleep(60*10)#wait 10 min
    except Exception as e:
        logger.error(f"Critical error in processing task: {e}")    
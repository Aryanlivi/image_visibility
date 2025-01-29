import subprocess
import os
from datetime import datetime
import logging
from .utils import get_current_datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YoutubeHandler:
    def __init__(self, url, output_dir):
        self.url = url
        self.output_dir = output_dir

    def create_dir(self):
        """
        Creates a directory for saving the screenshot.
        Returns the full path for the screenshot file.
        """
        try:
            # Create the base output directory if it doesn't exist
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            # Create a subfolder based on the current date (UTC)
            day_folder = get_current_datetime().strftime("%Y-%m-%d")
            day_folder_path = os.path.join(self.output_dir, day_folder)
            if not os.path.exists(day_folder_path):
                logger.info("Creating folder...")
                os.makedirs(day_folder_path)
            else:
                logger.info(f"Folder {day_folder_path} already exists.")

            # Generate a unique file name for the screenshot
            sanitized_datetime = get_current_datetime().strftime("%Y-%m-%d_%H-%M-%S")
            saving_dir = os.path.join(day_folder_path, f"{sanitized_datetime}.jpg")
            return saving_dir
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return None

    def get_stream_url(self):
        """
        Extracts the direct video stream URL using yt-dlp.
        """
        try:
            command = ["yt-dlp", "-g", "-f", "best", self.url]
            logger.info("Extracting video stream URL...")
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            stream_url = result.stdout.strip()
            logger.info("Stream URL extracted successfully.")
            return stream_url
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting video stream URL: {e}")
            return None

    def capture_screenshot(self):
        """
        Captures a single screenshot from the video stream.
        Returns the saving directory and capture time as a tuple.
        """
        saving_dir = self.create_dir()
        if not saving_dir:
            logger.error("Invalid saving directory")
            return None, None

        stream_url = self.get_stream_url()
        if not stream_url:
            logger.error("Failed to get stream URL")
            return None, None
        capture_time = get_current_datetime().isoformat()

        command = [
            "ffmpeg",
            "-y",  # Overwrite the file if it exists
            "-loglevel", "error",  # Suppress unnecessary output
            "-i", stream_url,  # Input stream URL
            "-frames:v", "1",  # Capture a single frame
            "-q:v", "2",  # Set image quality (lower is better)
            saving_dir,  # Output file
        ]

        try:
            logger.info(f"Capturing screenshot at {capture_time}...")
            subprocess.run(command, check=True)
            logger.info(f"Screenshot saved to {saving_dir} at {capture_time}.")
            return saving_dir, capture_time
        except subprocess.CalledProcessError as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None, None


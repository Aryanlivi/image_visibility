import base64
import piexif
from PIL import Image
import json
from datetime import datetime
import os
from decouple import config
import logging
from ftplib import FTP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def degrees_to_direction(degrees):
    COMPASS_DIRECTIONS = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    
    compass_directions_count = len(COMPASS_DIRECTIONS)
    compass_direction_arc = 360 / compass_directions_count
    return COMPASS_DIRECTIONS[int(degrees / compass_direction_arc) % compass_directions_count]

def decdeg2dms(dd):
    negative = dd < 0
    dd = abs(dd)
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    if negative:
        if degrees > 0: degrees = -degrees
        elif minutes > 0: minutes = -minutes
        else: seconds = -seconds
    return (int(degrees), int(minutes), seconds)


class ImageHandler:
    def __init__(self, img_path):
        self.maker_note = None
        self.exif_dict = {}
        self.img = None
        self.img_path=img_path
        # Open the image
        try:
            self.img = Image.open(self.img_path)
        except Exception as e:
            logger.error(f"Error: {e}")

    def get_exif_dict(self):
        return self.exif_dict

    def create_encoded_maker_note(self, device_id, devicecode, album_code, latitude, longitude, altitude, datetime_taken, imageowner):
        self.maker_note = {
            "device_id": device_id,
            "devicecode": devicecode,
            "album_code": album_code,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "date_taken": datetime_taken,
            "imageowner": imageowner
        }
        maker_note_json = json.dumps(self.maker_note)
        # Encode the JSON string in base64
        maker_note_base64 = base64.b64encode(maker_note_json.encode('utf-8'))
        
        return maker_note_base64

    def add_metadata_and_save(self, maker_note_base64, firstangle, lastangle, artist='RTS_V2'):
        if self.maker_note and self.img:
            # logger.info("Adding Metadata...")
            latDeg, latMin, latSec = decdeg2dms(self.maker_note['latitude'])
            longDeg, longMin, longSec = decdeg2dms(self.maker_note['longitude'])
            latSec = int(str(round(latSec, 2)).replace(".", ""))
            longSec = int(str(round(longSec, 2)).replace(".", ""))
            w, h = self.img.size

            zeroth_ifd = {
                piexif.ImageIFD.Make: u"Youtube",
                piexif.ImageIFD.Model: u"Screenshot",
                piexif.ImageIFD.Artist: artist,
                piexif.ImageIFD.XResolution: (w, 1),
                piexif.ImageIFD.YResolution: (h, 1),
            }
            exif_ifd = {
                piexif.ExifIFD.DateTimeOriginal: self.maker_note['date_taken'],
                piexif.ExifIFD.MakerNote: maker_note_base64,
            }

            gps_ifd = {
                piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
                piexif.GPSIFD.GPSLatitude: ((latDeg, 1), (latMin, 1), (latSec, 100)),
                piexif.GPSIFD.GPSLatitudeRef: b'N' if self.maker_note['latitude'] >= 0 else b'S',
                piexif.GPSIFD.GPSLongitude: ((longDeg, 1), (longMin, 1), (longSec, 10)),
                piexif.GPSIFD.GPSLongitudeRef: b'E' if self.maker_note['longitude'] >= 0 else b'W',
                piexif.GPSIFD.GPSAltitude: (int(self.maker_note['altitude']) * 100, 100),
                piexif.GPSIFD.GPSAltitudeRef: 0,  # from SeaLevel: 0
                piexif.GPSIFD.GPSImgDirection: ((firstangle, 1), (lastangle, 1)),
                piexif.GPSIFD.GPSImgDirectionRef: degrees_to_direction(firstangle),
            }

            self.exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd}
            exif_bytes = piexif.dump(self.exif_dict)

            #OVERRIDE THE IMAGE
            self.img.save(self.img_path, exif=exif_bytes)
            
        
            # Convert to epoch time
            epoch_time = int(datetime.fromisoformat(self.maker_note['date_taken']).timestamp())
            directory = os.path.dirname(self.img_path)  # Get the directory of the original file
            new_file_name = os.path.join(directory, f"{self.maker_note['devicecode']}_{epoch_time}.jpg")
            
            # Rename the file (overwrite the original file)
            os.rename(self.img_path, new_file_name)
            logger.debug(f"Metadata added and Image renamed to: {new_file_name}")
            return new_file_name
            
    def delete_file_locally(self,file_name):
        if os.path.exists(file_name):
            os.remove(file_name)  # Delete the local file
            # logger.info(f"Deleted local file: {file_name}")

                
            
    def upload_to_ftp(self,file_to_upload):
        ftp_server = config('ftp_server')
        ftp_username = config('ftp_username')
        ftp_password = config('ftp_password')
        remote_directory = config('remote_dir')

        try:
            # Connect to the FTP server
            ftp = FTP(ftp_server)
            ftp.login(user=ftp_username, passwd=ftp_password)
            logger.info(f"Connected to FTP server: {ftp_server}")

            # Change to the target directory
            ftp.cwd(remote_directory)
            logger.debug(f"Changed to directory: {remote_directory}")
            # Extract the file name from the full path
            file_name = os.path.basename(file_to_upload)
            
            # Upload the file
            with open(file_to_upload, "rb") as file:
                ftp.storbinary(f"STOR {file_name}", file)
                logger.info(f"Uploaded file: {file_name}")
            
            self.delete_file_locally(file_name=file_to_upload)
            # Close the connection
            ftp.quit()
            logger.info("FTP connection closed.")

        except Exception as e:
            logger.error(f"An error occurred during FTP upload: {e}")
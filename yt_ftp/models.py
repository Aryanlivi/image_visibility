from django.db import models
from django_celery_beat.models import PeriodicTask
from cryptography.fernet import Fernet
import base64
from django.conf import settings

class URL(models.Model):
    url = models.URLField(unique=True)
    name = models.CharField(max_length=50,db_index=True)  
    active =models.BooleanField(default=True)
    
    # Store the capture interval as seconds
    capture_interval = models.PositiveIntegerField(
        help_text="Enter the interval as total seconds"
    )
    last_run=models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class ImageMetadata(models.Model):
    url = models.OneToOneField(
        URL, 
        on_delete=models.CASCADE,  # Ensures that the image metadata is deleted when the URL is deleted
        related_name='image_metadata', 
        null=False, blank=False  # This is required as it is a one-to-one relationship
    )
    device_id = models.IntegerField(unique=True)  # Use device_id as the primary key
    devicecode = models.CharField(max_length=100)
    album_code = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField() 
    imageowner = models.CharField(max_length=100)
    angle = models.FloatField()
    def __str__(self): 
        return f"Metadata for {self.url.name}"


class CustomPeriodicTask(PeriodicTask):
    #customperiodictask_set is the reverse relation created automatically.
    url_instance = models.ForeignKey(URL, on_delete=models.CASCADE, null=True, blank=True)
    # last_run_at=models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.name}"
    class Meta: 
        verbose_name = "Custom Periodic Task"
        
    
    
# Generate a secret key once and store it securely (e.g., in .env)
SECRET_KEY = settings.SECRET_KEY  # Use Django's SECRET_KEY or a separate encryption key

def get_cipher():
    key = base64.urlsafe_b64encode(SECRET_KEY[:32].encode())  # Ensure a 32-byte key
    return Fernet(key)

class FTPConfig(models.Model):
    ftp_server = models.CharField(max_length=255)
    ftp_username = models.CharField(max_length=255)
    ftp_password_encrypted = models.BinaryField()  # Store encrypted password
    remote_directory = models.CharField(max_length=255)
    urls = models.ManyToManyField("URL", related_name="ftp_configs")  # Many-to-Many relation

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        """Encrypt and store password"""
        cipher = get_cipher()
        self.ftp_password_encrypted = cipher.encrypt(raw_password.encode())

    def get_password(self):
        """Decrypt and return password"""
        cipher = get_cipher()
        return cipher.decrypt(self.ftp_password_encrypted).decode()

    def __str__(self):
        return f"{self.ftp_server} ({self.remote_directory})"
from django.db import models

class URL(models.Model):
    url = models.URLField(unique=True)
    name = models.CharField(max_length=50,db_index=True)


    # Status of the URL processing
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',  # Default value when the status is not specified
    )
    
    # Store the capture interval as seconds
    capture_interval = models.PositiveIntegerField(
        help_text="Enter the interval as total seconds"
    )
    
    
    last_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url
    
class ImageMetadata(models.Model):
    url = models.OneToOneField(
        URL, 
        on_delete=models.CASCADE,  # Ensures that the image metadata is deleted when the URL is deleted
        related_name='image_metadata', 
        null=False, blank=False  # This is required as it is a one-to-one relationship
    )
    device_id = models.IntegerField(primary_key=True)  # Use device_id as the primary key
    devicecode = models.CharField(max_length=100)
    album_code = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    imageowner = models.CharField(max_length=100)
    angle = models.FloatField()
    def __str__(self):
        return f"Metadata for {self.devicecode}"

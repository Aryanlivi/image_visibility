from django.contrib import admin
from .models import URL, ImageMetadata

class ImageMetadataInline(admin.StackedInline):  
    model = ImageMetadata
    readonly_fields = []  
    extra = 1  # Since it's OneToOne, no extra forms are needed

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    inlines = [ImageMetadataInline]  
    list_display = ('url', 'name', 'active', 'capture_interval', 'last_run', 'created_at', 'updated_at')
    search_fields = ('url', 'name')

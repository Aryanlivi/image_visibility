from django.contrib import admin
from django_celery_beat.admin import PeriodicTaskAdmin
from .models import URL, ImageMetadata,CustomPeriodicTask


from django_celery_beat.models import PeriodicTask
PeriodicTask._meta.managed = False

class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    list_display = ('url_instance', 'enabled', 'last_run_at', 'date_changed')

admin.site.register(CustomPeriodicTask, CustomPeriodicTaskAdmin)
class ImageMetadataInline(admin.StackedInline):  
    model = ImageMetadata
    readonly_fields = []  
    extra = 1  # Since it's OneToOne, no extra forms are needed

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    inlines = [ImageMetadataInline]  
    list_display = ('url', 'name', 'active', 'capture_interval', 'last_run', 'created_at', 'updated_at')
    search_fields = ('url', 'name')


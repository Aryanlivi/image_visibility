from django.contrib import admin
from django_celery_beat.admin import PeriodicTaskAdmin
from .models import URL, ImageMetadata,CustomPeriodicTask,FTPConfig


from django_celery_beat.models import PeriodicTask
PeriodicTask._meta.managed = False

class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    list_display = ('url_instance', 'enabled', 'last_run_at', 'date_changed')

admin.site.register(CustomPeriodicTask, CustomPeriodicTaskAdmin)
class ImageMetadataInline(admin.StackedInline):  
    model = ImageMetadata
    readonly_fields = []  
    extra = 1  # Since it's OneToOne, no extra forms are needed

class FTPConfigsInline(admin.StackedInline):  
    model = FTPConfig.urls.through  # This is the intermediary model for the ManyToMany relation
    readonly_fields = []  
    extra = 1  # Since it's OneToOne, no extra forms are needed
@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    inlines = [ImageMetadataInline,FTPConfigsInline]  
    list_display = ('url', 'name', 'active', 'capture_interval', 'last_run', 'created_at', 'updated_at')
    search_fields = ('url', 'name')

@admin.register(FTPConfig)
class FTPConfig(admin.ModelAdmin):
    list_display = ('ftp_username', 'ftp_password_encrypted', 'remote_directory')
    search_fields = ('ftp_username', 'remote_directory')
    
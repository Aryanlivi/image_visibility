from django.apps import AppConfig
from django.db.models.signals import post_migrate 

class YtFtpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'yt_ftp'

    def ready(self) -> None:
        import yt_ftp.signals.handlers



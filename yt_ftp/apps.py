from django.apps import AppConfig


class YtFtpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'yt_ftp'
    
    def ready(self) -> None:
        import yt_ftp.signals.handlers

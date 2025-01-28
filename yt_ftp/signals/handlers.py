from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from yt_ftp.models import URL

@receiver(post_save, sender=URL)
def start_celery_task(sender, **kwargs):
    url_instance = kwargs['instance']
    print("POST SAVE CALLED!")
    print(url_instance)
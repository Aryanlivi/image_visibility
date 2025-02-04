from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_celery_beat.models import IntervalSchedule
from yt_ftp.models import URL, ImageMetadata, CustomPeriodicTask
import json
from yt_ftp.tasks import process_url 
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=URL)
@receiver(post_save, sender=ImageMetadata)
def start_celery_task(sender, instance, created, **kwargs):
    """Handle creation or update of URL/ImageMetadata."""
    url_instance = instance.url if sender == ImageMetadata else instance
    active = url_instance.active
    interval = url_instance.capture_interval

    if created and active:
        process_url.delay(url_instance.id)  # Run task immediately for active instances
        schedule_task(url_instance.id, interval) 
    elif not active:
        disable_task(url_instance)  # Disable task for inactive instance
    elif not created:#this means the signal was update.
        update_or_schedule_task(url_instance, interval)
def update_or_schedule_task(url_instance, interval):
    """Update or create a periodic task for the given URL instance."""
    task = CustomPeriodicTask.objects.filter(url_instance=url_instance).first()

    if task:
        # Update existing task
        if task.interval.every != interval:
            task.interval.every = interval
            task.interval.save()
        if not task.enabled and url_instance.active:
            task.enabled = True  # Re-enable if inactive
        task.args = json.dumps([url_instance.id])
        task.save()
    else:
        # Create a new scheduled task
        schedule_task(url_instance.id, interval, enable=url_instance.active)


def schedule_task(instance_id, interval, enable=True):
    """Create a new periodic task with the specified interval."""
    url_instance = URL.objects.get(pk=instance_id)
    task_name = f"Process_URL_{url_instance}"

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=interval, period=IntervalSchedule.SECONDS
    )

    CustomPeriodicTask.objects.create(
        name=task_name,
        task='yt_ftp.tasks.process_url',
        interval=schedule,
        args=json.dumps([instance_id]),
        url_instance=url_instance,
        enabled=enable,  # Enable only if active
    )

def disable_task(url_instance):
    """Disable the periodic task for inactive instances."""
    task = CustomPeriodicTask.objects.filter(url_instance=url_instance).first()
    if task:
        task.enabled = False
        task.save()

def delete_scheduled_task(url_instance):
    """Delete the scheduled periodic task for the given URL instance."""
    task = CustomPeriodicTask.objects.filter(url_instance=url_instance).first()
    if task:
        task.delete()
        task.interval.delete()

@receiver(post_delete, sender=URL)
@receiver(post_delete, sender=ImageMetadata)
def delete_task_on_instance_delete(sender, instance, **kwargs):
    """Delete task when the instance is deleted."""
    url_instance = instance.url if isinstance(instance, ImageMetadata) else instance
    delete_scheduled_task(url_instance)

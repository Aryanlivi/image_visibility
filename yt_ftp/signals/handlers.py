from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from yt_ftp.models import URL, ImageMetadata
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@receiver(post_save, sender=URL)
@receiver(post_save, sender=ImageMetadata)
def start_celery_task(sender, instance, created, **kwargs):
    logger.info(f"Signal triggered for {sender.__name__}: {instance}, created: {created}")
    if sender == URL:
        interval = instance.capture_interval 
        task_name = f"process-url-every-{interval}-seconds-for-{instance.name}"
        schedule_task(instance.id, interval,task_name)
    elif sender == ImageMetadata:
        interval = instance.url.capture_interval
        task_name = f"process-url-every-{interval}-seconds-for-{instance.url.name}"
        schedule_task(instance.url.id, interval,task_name)


def schedule_task(instance_id, interval,task_name):
    """Creates or updates a Celery Beat PeriodicTask with the given interval."""
    try:
        if not interval or interval <= 0:
            logger.error(f"Invalid interval ({interval}) for instance {instance_id}.")
            return

        # Ensure IntervalSchedule exists or create it
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=interval,  
            period=IntervalSchedule.SECONDS
        )
        
        logger.info(f"SENT ID : {instance_id}")
        # Create or update the PeriodicTask
        periodic_task, created = PeriodicTask.objects.get_or_create(
            name=task_name,
            defaults={
                'task': 'yt_ftp.tasks.process_url', 
                'interval': schedule,
                'args': json.dumps([instance_id]), 
                'enabled': True,
            } 
        )

        if not created:  # If task exists, update it
            periodic_task.interval = schedule
            periodic_task.enabled = True
            periodic_task.args = json.dumps([instance_id])
            periodic_task.save()
            logger.info(f"Updated existing task: {task_name} with interval {interval} seconds.")
        else:
            logger.info(f"Created new task: {task_name} with interval {interval} seconds.")

    except Exception as e:
        logger.error(f"Error scheduling task for instance {instance_id}: {e}")




@receiver(post_delete, sender=URL)
@receiver(post_delete, sender=ImageMetadata)
def delete_scheduled_task(sender, instance, **kwargs):
    """Deletes the PeriodicTask and IntervalSchedule when a URL or ImageMetadata instance is deleted."""
    try:
        if sender == URL:
            interval = instance.capture_interval
            task_name = f"process-url-every-{interval}-seconds-for-{instance.name}"
        elif sender == ImageMetadata:
            interval = instance.url.capture_interval
            task_name = f"process-url-every-{interval}-seconds-for-{instance.url.name}"
        
        # Delete the associated PeriodicTask
        deleted, _ = PeriodicTask.objects.filter(name=task_name).delete()
        if deleted:
            logger.info(f"Deleted PeriodicTask: {task_name}")

        # Check if any other task is using the same interval
        if not PeriodicTask.objects.filter(interval__every=interval, interval__period=IntervalSchedule.SECONDS).exists():
            IntervalSchedule.objects.filter(every=interval, period=IntervalSchedule.SECONDS).delete()
            logger.info(f"Deleted IntervalSchedule with interval {interval} seconds.")

    except Exception as e:
        logger.error(f"Error deleting scheduled task for instance {instance.id}: {e}")
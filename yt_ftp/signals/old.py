from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_celery_beat.models import  IntervalSchedule
from yt_ftp.models import URL, ImageMetadata,CustomPeriodicTask
import logging
import json
from yt_ftp.tasks import process_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@receiver(post_save, sender=URL)
@receiver(post_save, sender=ImageMetadata)
def start_celery_task(sender, instance, created, **kwargs):
    logger.info(f"Signal triggered for {sender.__name__}: {instance}, created: {created}")
    interval = instance.capture_interval if sender == URL else instance.url.capture_interval
    active= instance.active if sender == URL else instance.url.active
    if created and active:
        process_url.delay(instance.id if sender == URL else instance.url.id)
        logger.info(f"Ran Celery task immediately for: {instance.url.name}")
    elif not active:  
        pass
        # logger.info("----------DELETED FOR INACTIVE----------")  
        # delete_scheduled_task(task_name)
    # task_name = f"Process:{instance.name if sender == URL else instance.url.name} in interval {interval} seconds"
    
    # Check if the interval has changed
    elif not created:
        update_task_interval(instance=instance)
        if active:
            schedule_task()
        else:
            pass
    
    
def update_task_interval(instance):
    try:
        update_task_interval(instance)
        schedule_task(instance.id if sender == URL else instance.url.id, interval,is_updated=True)
    except CustomPeriodicTask.DoesNotExist:
        # If the task doesn't exist yet, create a new one
        schedule_task(instance.id if sender == URL else instance.url.id, interval)
        logger.info(f"Created new task: {url_instance} with interval {interval} seconds.")
    
def schedule_task(instance_id, interval,is_updated=False):
    """Creates or updates a Celery Beat PeriodicTask with the given interval."""
    try:

        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=interval,
            period=IntervalSchedule.SECONDS
        )

        url_instance = URL.objects.get(pk=instance_id)  # Fetch the URL instance

        periodic_task, created = CustomPeriodicTask.objects.get_or_create(
            name=task_name,
            defaults={
                'task': 'yt_ftp.tasks.process_url',
                'interval': schedule,
                'args': json.dumps([instance_id]), 
                'enabled': True,
                'url_instance': url_instance  # Link to URL instance
            }
        )

        if not created:
            periodic_task.interval = schedule
            periodic_task.enabled = True
            periodic_task.args = json.dumps([instance_id])
            periodic_task.url_instance = url_instance  # Ensure linkage
            periodic_task.save()
            logger.info(f"Updated existing task: {task_name} with interval {interval} seconds.")
        else:
            logger.info(f"Created new custom task: {task_name} with interval {interval} seconds.")

    except Exception as e:
        logger.error(f"Error scheduling task for instance {instance_id}: {e}")

def delete_scheduled_task(task_name):
    """Deletes the scheduled periodic task and its associated interval."""
    try:
        # Find the task in CustomPeriodicTask
        task = CustomPeriodicTask.objects.filter(name=task_name).first()
        logger.info(f"TASK: {task}")

        if task:
            interval = task.interval  # Get the associated interval
            task.delete()  # Delete the task
            logger.info(f"Deleted task: {task_name}")

            # Delete the interval as well
            interval.delete()
            logger.info(f"Deleted associated interval: {interval}")
        else:
            logger.info(f"No task found with name: {task_name}")

    except Exception as e:
        logger.error(f"Error deleting scheduled task {task_name}: {e}")

        logger.error(f"Error deleting scheduled task {task_name}: {e}")
        
@receiver(post_delete, sender=URL)
@receiver(post_delete, sender=ImageMetadata)
def delete_task_on_instance_delete(sender, instance, **kwargs):
    """Deletes the task when the instance is deleted."""
    interval = instance.capture_interval if sender == URL else instance.url.capture_interval
    task_name = f"Process:{instance.name if sender == URL else instance.url.name} in interval {interval} seconds"
    delete_scheduled_task(task_name)

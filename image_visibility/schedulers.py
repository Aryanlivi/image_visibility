from django_celery_beat.schedulers import DatabaseScheduler
from django_celery_beat.models import PeriodicTask
from yt_ftp.models import CustomPeriodicTask

class CustomScheduler(DatabaseScheduler):
    def setup_periodic_tasks(self, *args, **kwargs):
        # Override to use your custom PeriodicTask model
        super().setup_periodic_tasks(*args, **kwargs)


    def get_task_model(self):
        """
        Use the custom task model instead of the default one.
        """
        return CustomPeriodicTask

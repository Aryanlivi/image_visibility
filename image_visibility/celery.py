from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "image_visibility.settings")


app = Celery("image_visibility")

# Load task modules from all registered Django app configs
app.config_from_object("django.conf:settings", namespace="CELERY")

# app.conf.beat_schedule = settings.CELERY_BEAT_SCHEDULE
# app.conf.timezone = 'UTC'  # or your preferred timezone
app.conf.broker_url = settings.CELERY_BROKER_URL  # Set explicitly

#configure autoscaling
app.conf.worker_autoscaler = settings.CELERY_WORKER_AUTOSCALE
app.conf.worker_concurrency = settings.CELERY_WORKER_CONCURRENCY

# Auto-discover tasks in Django apps
app.autodiscover_tasks()

# Set the Celery Beat scheduler
app.conf.beat_scheduler = 'image_visibility.schedulers.CustomScheduler'
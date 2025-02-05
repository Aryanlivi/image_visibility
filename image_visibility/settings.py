"""
Django settings for image_visibility project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from decouple import config
import os
# from celery.schedules import crontab
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-t7%%#wit%36w*v&9*%vig+-e_$neb4-jhl=#tv#ykdqg!-r*y$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ["*"]

# Celery Configuration
CELERY_BROKER_URL = "redis://localhost:6379/0"  # Use Redis for queuing
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# Store Celery task results in PostgreSQL
CELERY_RESULT_BACKEND = "django-db"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


CELERY_WORKER_CONCURRENCY = 4  # Set fixed number of workers (instead of using --concurrency on command line)

# Optionally, configure autoscaling if you prefer this way
CELERY_WORKER_AUTOSCALE = (10, 4)  # Maximum 10, minimum 4 workers 
CELERY_BEAT_PERIODIC_TASK_MODEL = 'yt_ftp.models.CustomPeriodicTask'
CELERY_BEAT_SCHEDULER = 'image_visibility.schedulers.CustomScheduler'


#REST FRAMEWORK AND FILTERS:

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "corsheaders",
]

MY_APPS=[
    "django_celery_beat",
    "django_celery_results",
    "debug_toolbar",
    "rest_framework",
    "yt_ftp",
    "django_filters",
]

INSTALLED_APPS+=MY_APPS

MY_MIDDLEWARE=["debug_toolbar.middleware.DebugToolbarMiddleware",
            "image_visibility.middleware.SecureHeadersMiddleware"
            ]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
MIDDLEWARE+=MY_MIDDLEWARE
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]
ROOT_URLCONF = 'image_visibility.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'image_visibility.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("LOCAL_DB_NAME"),
        "USER": config("LOCAL_DB_USER"),
        "PASSWORD": config('LOCAL_DB_PASS'),
        "HOST": config("LOCAL_DB_HOST"),
        "PORT": config("LOCAL_DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "yt_ftp", "static")]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SECURE_SSL_REDIRECT = True  # Redirect HTTP requests to HTTPS
SECURE_HSTS_SECONDS = 31536000  # Enable HTTP Strict Transport Security
SECURE_HSTS_PRELOAD = True  # Optionally preload HSTS (ensure it's used for all subdomains)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Apply HSTS to all subdomains

# Generated by Django 5.1.5 on 2025-01-31 06:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_beat', '0019_alter_periodictasks_options'),
        ('yt_ftp', '0002_remove_url_status_url_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomPeriodicTask',
            fields=[
                ('periodictask_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='django_celery_beat.periodictask')),
                ('url_instance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='yt_ftp.url')),
            ],
            options={
                'verbose_name': 'Custom Periodic Task',
            },
            bases=('django_celery_beat.periodictask',),
        ),
    ]

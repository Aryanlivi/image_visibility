# Generated by Django 5.1.5 on 2025-01-28 04:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('name', models.CharField(db_index=True, max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('stopped', 'Stopped')], default='pending', max_length=20)),
                ('capture_interval', models.PositiveIntegerField(help_text='Enter the interval as total seconds')),
                ('last_run', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImageMetadata',
            fields=[
                ('device_id', models.IntegerField(primary_key=True, serialize=False)),
                ('devicecode', models.CharField(max_length=100)),
                ('album_code', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('altitude', models.FloatField()),
                ('imageowner', models.CharField(max_length=100)),
                ('angle', models.FloatField()),
                ('url', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='image_metadata', to='yt_ftp.url')),
            ],
        ),
    ]

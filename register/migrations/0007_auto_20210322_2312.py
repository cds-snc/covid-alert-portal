# Generated by Django 3.1.7 on 2021-03-22 23:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0006_auto_20210308_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='registrant',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

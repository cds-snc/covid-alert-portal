# Generated by Django 3.2 on 2021-04-30 16:48

from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension


class Migration(migrations.Migration):

    dependencies = [
        ('outbreaks', '0001_initial'),
    ]

    operations = [
        UnaccentExtension()
    ]
# Generated by Django 3.1.7 on 2021-03-18 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0008_auto_20210318_1825'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailconfirmation',
            old_name='created',
            new_name='created_at',
        ),
    ]

# Generated by Django 3.2 on 2021-04-07 16:16

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0003_location_registrant'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='contact_phone_ext',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=20, region=None),
        ),
    ]

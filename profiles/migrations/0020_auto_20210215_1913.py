# Generated by Django 3.1.6 on 2021-02-15 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('profiles', '0019_healthcareprovince_sms_enabled'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='healthcareuser',
            options={'permissions': [('can_send_alerts', 'Can send outbreak alerts')]},
        ),
        migrations.AddField(
            model_name='healthcareuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='healthcareuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]

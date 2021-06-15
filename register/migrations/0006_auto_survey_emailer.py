# Generated by Django 3.2.3 on 2021-06-15 19:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('register', '0005_locationsummary'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(verbose_name='General Survey URL')),
                ('title', models.CharField(max_length=200, verbose_name='Survey Title')),
                ('en_notify_template_id', models.CharField(max_length=200, verbose_name='English Notify Template ID')),
                ('fr_notify_template_id', models.CharField(max_length=200, verbose_name='French Notify Template ID')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='registrant',
            name='language_cd',
            field=models.CharField(default='en', max_length=2),
        ),
        migrations.CreateModel(
            name='RegistrantSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_ts', models.DateTimeField(blank=True, null=True, verbose_name='Sent Timestamp')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('registrant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='register.registrant')),
                ('sent_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('survey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='register.survey')),
            ],
        ),
    ]

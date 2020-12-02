from django.contrib import admin
from .models import GoogleAnalytics
from solo.admin import SingletonModelAdmin

admin.site.register(GoogleAnalytics, SingletonModelAdmin)

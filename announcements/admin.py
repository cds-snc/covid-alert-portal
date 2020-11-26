from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "title_en",
        "content_en",
        "title_fr",
        "content_fr",
        "is_active",
        "level",
        "for_user",
        "creation_date",
    )
    list_filter = ("level", "creation_date")
    readonly_fields = ["creation_date"]
    fieldsets = (
        (
            None,
            {"fields": ["title_en", "content_en", "title_fr", "content_fr", "level"]},
        ),
        (
            "Display Options",
            {
                "fields": [
                    "is_active",
                    "for_user",
                    "dismissable",
                    "publish_start",
                    "publish_end",
                ]
            },
        ),
    )

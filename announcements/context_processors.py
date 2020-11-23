from .models import Announcement
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
import datetime


def announcement(request):
    """
    Adds the active announcements to the context for users with an active session
    """
    todays_date = datetime.date.today()
    logged_in = request.user.is_authenticated
    if logged_in:
        available_announcements = (
            Announcement.objects.filter(Q(for_user=request.user) | Q(site_wide=True))
            .filter(Q(display=True) & Q(publish_start__lte=todays_date))
            .filter(Q(publish_end__gte=todays_date) | Q(publish_end=None))
        )

        if available_announcements.count() > 0:
            display_announcements = []
            for announcement in available_announcements:
                if request.LANGUAGE_CODE == "en":
                    display_announcements += [
                        {
                            "title": announcement.title_en,
                            "content": announcement.content_en,
                            "level": announcement.level,
                        }
                    ]
                elif request.LANGUAGE_CODE == "fr":
                    display_announcements += [
                        {
                            "title": announcement.title_fr,
                            "content": announcement.content_fr,
                            "level": announcement.level,
                        }
                    ]

            return {"announcements": display_announcements}

    return {"announcements": []}

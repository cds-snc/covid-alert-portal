import pytz
from django.conf import settings


class TZMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        browser_tz = request.COOKIES.get("browserTimezone")
        tz = None
        if browser_tz:
            try:
                tz = pytz.timezone(browser_tz)
            except pytz.UnknownTimeZoneError:
                pass
        if not tz:
            tz = pytz.timezone(settings.PORTAL_LOCAL_TZ)

        def convert_to_local_tz_from_utc(utc_dttm):
            return utc_dttm.astimezone(tz=tz)

        request.convert_to_local_tz_from_utc = convert_to_local_tz_from_utc

        response = self.get_response(request)
        return response

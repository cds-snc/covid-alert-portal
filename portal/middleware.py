import pytz
from pytz import UnknownTimeZoneError
from django.conf import settings


class TZMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        browser_tz = request.COOKIES.get('browserTimezone')
        tz = None
        if browser_tz:
            try:
                tz = pytz.timezone(browser_tz)
            except UnknownTimeZoneError:
                pass
        if not tz:
            tz = pytz.timezone(settings.PORTAL_LOCAL_TZ)

        def replace_to_local_tz(dttm):
            return dttm.replace(tzinfo=tz)
        def localize_dttm(dttm):
            return tz.localize(dttm)
        def convert_to_local_tz_from_utc(utc_dttm):
            return utc_dttm.astimezone(tz=tz)

        request.replace_to_local_tz = replace_to_local_tz
        request.localize_dttm = localize_dttm
        request.convert_to_local_tz_from_utc = convert_to_local_tz_from_utc

        response = self.get_response(request)
        return response

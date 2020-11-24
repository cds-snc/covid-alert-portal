from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import Announcement


class AnnouncementDismissView(SingleObjectMixin, View):
    model = Announcement

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        from_url = request.META['HTTP_REFERER']
        if self.object.dismissable:
            # get list from session and type it to set()
            excluded = set(request.session.get("excluded_announcements", []))
            excluded.add(self.object.pk)
            # force to list to avoid TypeError on set() json serialization
            request.session["excluded_announcements"] = list(excluded)
        return HttpResponseRedirect(from_url)


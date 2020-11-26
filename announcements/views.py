from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Announcement


class AnnouncementDismissView(SingleObjectMixin, View):
    model = Announcement

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        from_url = reverse("start")
        if request.META["HTTP_REFERER"]:
            from_url = request.META["HTTP_REFERER"]
        if self.object.dismissable:
            # get list from session and type it to set()
            excluded = set(request.session.get("excluded_announcements", []))
            excluded.add(self.object.pk)
            # force to list to avoid TypeError on set() json serialization
            request.session["excluded_announcements"] = list(excluded)
        return HttpResponseRedirect(from_url)

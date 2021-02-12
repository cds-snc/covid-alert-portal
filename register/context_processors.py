from django.utils.translation import gettext as _


def general_settings(request):
    return {"title_suffix": _("— Scan a place registration")}

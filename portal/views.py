from django.shortcuts import render


def permission_denied_view(request, exception=None):
    return render(request, "403.html", status=403)


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)


def internal_error(request):
    return render(request, "500.html", status=500)

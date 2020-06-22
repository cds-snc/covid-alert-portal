from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('', include('profiles.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^invitations/', include('invitations.urls', namespace='invitations')),
]

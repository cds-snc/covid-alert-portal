from django.urls import path, include, re_path
from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="landing")),
    path(
        "landing/",
        TemplateView.as_view(template_name="profiles/landing.html"),
        name="landing",
    ),
    path("code/", views.code, name="code"),
    path(
        "start/",
        login_required(TemplateView.as_view(template_name="profiles/start.html")),
        name="start",
    ),
    re_path(r"signup/$", views.SignUp.as_view(), name="signup"),
    # Removed for now
    # path('profiles/', views.UserListView.as_view(), name='profiles'),
    # url(
    #     r'profiles/(?P<pk>\w+)$',
    #     views.UserProfileView.as_view(),
    #     name='user_profile',
    # ),
    # url(r'profiles/(?P<pk>\w+)/edit$', views.UserEdit.as_view(), name='user_edit'),
    path("", include("django.contrib.auth.urls")),
]

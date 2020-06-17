from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'users/(?P<user_id>\w+)$',
        views.UserProfileView.as_view(),
        name='user_profile',
    ),
    path('', views.HomePageView.as_view(), name='home'),

]
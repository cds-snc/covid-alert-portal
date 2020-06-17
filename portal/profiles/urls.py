from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'profiles'

urlpatterns = [
    url(
        r'users/(?P<user_id>\w+)$',
        views.UserProfileView.as_view(),
        name='user_profile',
    ),
    path('', views.HomePageView.as_view(), name='home'),

    # default auth routes: https://docs.djangoproject.com/en/3.0/topics/auth/default/#module-django.contrib.auth.views
    # accounts/login/ [name='login']
    # accounts/logout/ [name='logout']
    # accounts/password_change/ [name='password_change']
    # accounts/password_change/done/ [name='password_change_done']
    # accounts/password_reset/ [name='password_reset']
    # accounts/password_reset/done/ [name='password_reset_done']
    # accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # accounts/reset/done/ [name='password_reset_complete']
    path('', include('django.contrib.auth.urls')),
]
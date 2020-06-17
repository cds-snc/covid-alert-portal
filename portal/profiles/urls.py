from django.urls import path, include
from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'users/(?P<user_id>\w+)$',
        views.UserProfileView.as_view(),
        name='user_profile',
    ),
    path('', views.HomePageView.as_view(), name='home'),
    path('signup/', views.SignUp.as_view(), name='signup'),

    # default auth routes: https://docs.djangoproject.com/en/3.0/topics/auth/default/#module-django.contrib.auth.views
    # /login/ [name='login']
    # /logout/ [name='logout']
    # /password_change/ [name='password_change']
    # /password_change/done/ [name='password_change_done']
    # /password_reset/ [name='password_reset']
    # /password_reset/done/ [name='password_reset_done']
    # /reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # /reset/done/ [name='password_reset_complete']
    path('', include('django.contrib.auth.urls')),
]
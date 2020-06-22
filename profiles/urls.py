from django.urls import path, include, re_path
from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [

    path('', RedirectView.as_view(pattern_name='start')),
    path('code/', views.code, name='code'),
    path('start/', login_required(TemplateView.as_view(template_name="profiles/start.html")), name='start'),
    path('profiles/', views.UserListView.as_view(), name='profiles'),
    url(
        r'profiles/(?P<pk>\w+)$',
        views.UserProfileView.as_view(),
        name='user_profile',
    ),
    url(r'profiles/(?P<pk>\w+)/edit$', views.UserEdit.as_view(), name='user_edit'),

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

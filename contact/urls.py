from django.urls import path
from django.views.generic import TemplateView
from .views import ContactFormView

app_name = 'contact'
urlpatterns = [
    path("", ContactFormView.as_view(), name='index'),
    path("success", TemplateView.as_view(template_name="contact/success.html"), name='success'),
]

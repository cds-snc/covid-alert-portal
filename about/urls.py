from django.urls import path
from django.views.generic import TemplateView

app_name = "about"
urlpatterns = [
    path("", TemplateView.as_view(template_name="about/1_index.html"), name="index"),
    path(
        "create-an-account",
        TemplateView.as_view(template_name="about/2_create_account.html"),
        name="create_account",
    ),
    path(
        "one-time-keys",
        TemplateView.as_view(template_name="about/3_one_time_keys.html"),
        name="one_time_keys",
    ),
    path(
        "give-a-key",
        TemplateView.as_view(template_name="about/4_give_a_key.html"),
        name="give_a_key",
    ),
    path(
        "help-patient-enter-key",
        TemplateView.as_view(template_name="about/5_help_patient_enter_key.html"),
        name="help_patient_enter_key",
    ),
    path(
        "sending-qr-alerts",
        TemplateView.as_view(template_name="about/6_sending_qr_alerts.html"),
        name="sending_qr_alerts",
    ),
    path(
        "admin-accounts",
        TemplateView.as_view(template_name="about/7_admin_accounts.html"),
        name="admin_accounts",
    ),
]

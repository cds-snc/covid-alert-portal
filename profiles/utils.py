from django_otp.plugins.otp_email.conf import settings as otp_settings

from django.conf import settings
from django.template.loader import get_template
from django.core.mail import send_mail
from .models import HealthcareUser

from django.contrib.sites.models import Site


def generate_2fa_code_for_device(email_device, user: HealthcareUser):
    # I cant use the email_device.generate_challenge() directly here,
    # I need to pass more context into the emails
    email_device.generate_token(valid_secs=otp_settings.OTP_EMAIL_TOKEN_VALIDITY)
    current_site = Site.objects.get_current()

    context = {
        "token": email_device.token,
        "full_name": user.name,
        "service_name": settings.SERVICE_NAME,
        "scheme": "https" if settings.SECURE_SSL_REDIRECT else "http",
        "http_host": current_site.domain,
    }
    body_html = get_template("otp/email/token.html").render(context)
    body_txt = get_template("otp/email/token.txt").render(context)

    send_mail(
        otp_settings.OTP_EMAIL_SUBJECT,
        body_txt,
        otp_settings.OTP_EMAIL_SENDER,
        [user.email],
        html_message=body_html,
    )


def generate_2fa_code(user: HealthcareUser):
    email_devices = user.emaildevice_set.all()
    # If the user has no email device, create one with his email
    if len(email_devices) == 0:
        email_device = user.emaildevice_set.create()
        generate_2fa_code_for_device(email_device, user)
    else:
        for email_device in email_devices:
            generate_2fa_code_for_device(email_device, user)

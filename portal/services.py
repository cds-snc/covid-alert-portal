"""
Custom services to be used with the dependency-injector package
"""
import logging
from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient


class NotifyService:
    """
    Service that wraps the Government of Canada Notifications API
    """

    def __init__(self, api_key=None, end_point=None):
        self.client = None
        if api_key is None or end_point is None:
            logging.info("Notifications disabled, no api key or end point specified.")
        else:
            self.client = NotificationsAPIClient(api_key, base_url=end_point)

    def send_email(self, address, template_id, details):
        """
        Send a new email using the GC notification client

        Args:
            address: The email address
            template_id: The id of the template to use
            details: Dictionary of personalization variables
        """
        if self.client:
            try:
                self.client.send_email_notification(
                    email_address=address,
                    template_id=template_id,
                    personalisation=details,
                )
            except HTTPError as e:
                raise Exception(e)
        else:
            logging.info(f"Notifications disabled. Otherwise would email: {address}.")

    def send_sms(self, phone_number, template_id, details):
        """
        Send a new SMS using the GC notification client

        Args:
            phone_number: The phone number to send to
            template_id: The id of the template to use
            details: Dictionary of personalization variables
        """
        if self.client:
            try:
                self.client.send_sms_notification(
                    phone_number=phone_number,
                    template_id=template_id,
                    personalisation=details,
                )
            except HTTPError as e:
                raise Exception(e)
        else:
            logging.info(
                f"Notifications disabled. Otherwise would text to: {phone_number}."
            )

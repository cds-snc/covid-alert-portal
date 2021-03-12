from django.test import TestCase, override_settings
from django.urls import reverse

from waffle.models import Switch

from . import forms
from .models import Registrant, Location, EmailConfirmation
from . import utils
from django.contrib.messages import get_messages
from portal.services import NotifyService
from portal import container
import base64
import xml.etree.cElementTree as et
import io
from nacl.encoding import Base64Encoder


def is_svg(contents):
    tag = None
    f = io.BytesIO(contents.encode())
    try:
        for event, el in et.iterparse(f, ("start",)):
            tag = el.tag
            break
    except et.ParseError:
        pass
    return tag == "{http://www.w3.org/2000/svg}svg"


def is_base64(sb):
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, "ascii")
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False


class RegisterView(TestCase):
    def test_start_page(self):
        response = self.client.get(reverse("register:start"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register/start.html")

    def test_email_page(self):
        response = self.client.get(reverse("register:registrant_email"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register/registrant_email.html")

    def test_name_page(self):
        r = Registrant.objects.create(email="test@test.com")
        session = self.client.session
        session["registrant_id"] = str(r.id)
        session.save()

        response = self.client.get(reverse("register:registrant_name"))
        self.assertEqual(response.status_code, 200)

    def test_confirmation_page_logged_in(self):
        email = "test@test.com"
        r = Registrant.objects.create(email=email)

        # add id and email to session (happens at confirmation)
        session = self.client.session
        session["registrant_id"] = str(r.id)
        session["registrant_email"] = r.email
        session.save()

        response = self.client.get(reverse("register:confirmation"))
        self.assertEqual(response.status_code, 200)


class RegisterEmailConfirmation(TestCase):
    def setUp(self):
        container.notify_service.override(NotifyService())  # Prevent sending emails

    def test_email_form_empty(self):
        form = forms.EmailForm(data={})

        self.assertEqual(form.errors["email"], ["This field is required."])

    def test_can_confirm_email(self):
        email = "test@test.com"
        # submit email
        response = self.client.post(
            reverse("register:registrant_email"), data={"email": email}
        )
        self.assertEqual(response.status_code, 302)

        # confirmation screen
        response = self.client.get(reverse("register:email_submitted"))

        self.assertContains(response, "Confirm your email address")
        self.assertContains(response, email)

        # check the confirmation record
        confirm = EmailConfirmation.objects.get(email=email)
        self.assertEquals(confirm.email, email)

        # generate the confirmation link
        confirm_url = reverse(
            "register:email_confirm",
            kwargs={"pk": confirm.pk},
        )

        # visit the confirmation link
        self.client.get(confirm_url)

        # confirmation record should be deleted
        self.assertIsNone(
            EmailConfirmation.objects.filter(email=email).first(),
        )

        # email confirmed, should be able to get to the name step
        self.client.get(reverse("register:registrant_name"))
        self.assertEqual(response.status_code, 200)


class RegisterConfirmedEmailRequiredPages(TestCase):
    def test_registrant_name_not_logged_in(self):
        response = self.client.get(reverse("register:registrant_name"))
        self.assertRedirects(response, reverse("register:registrant_email"))
        message = list(get_messages(response.wsgi_request))[0]
        self.assertEqual(message.tags, "error")

    def test_location_address_not_logged_in(self):
        response = self.client.get(
            reverse("register:location_step", kwargs={"step": "address"})
        )
        self.assertRedirects(response, reverse("register:registrant_email"))
        message = list(get_messages(response.wsgi_request))[0]
        self.assertEqual(message.tags, "error")

    def test_location_category_not_logged_in(self):
        response = self.client.get(
            reverse("register:location_step", kwargs={"step": "category"})
        )
        self.assertRedirects(response, reverse("register:registrant_email"))
        message = list(get_messages(response.wsgi_request))[0]
        self.assertEqual(message.tags, "error")

    def test_location_name_not_logged_in(self):
        response = self.client.get(
            reverse("register:location_step", kwargs={"step": "name"})
        )
        self.assertRedirects(response, reverse("register:registrant_email"))
        message = list(get_messages(response.wsgi_request))[0]
        self.assertEqual(message.tags, "error")

    def test_location_contact_not_logged_in(self):
        response = self.client.get(
            reverse("register:location_step", kwargs={"step": "contact"})
        )
        self.assertRedirects(response, reverse("register:registrant_email"))
        message = list(get_messages(response.wsgi_request))[0]
        self.assertEqual(message.tags, "error")

    def test_location_summary_not_logged_in(self):
        response = self.client.get(
            reverse("register:location_step", kwargs={"step": "summary"})
        )
        self.assertRedirects(response, reverse("register:registrant_email"))
        message = list(get_messages(response.wsgi_request))[0]
        self.assertEqual(message.tags, "error")

    def test_confirmation_not_logged_in(self):
        response = self.client.get(reverse("register:confirmation"))
        self.assertRedirects(response, reverse("register:registrant_email"))
        message = list(get_messages(response.wsgi_request))[0]
        self.assertEqual(message.tags, "error")


class RegisterLocationDetailsValidation(TestCase):
    def test_location_category_empty(self):
        form = forms.LocationCategoryForm(data={})

        self.assertEqual(form.errors["category"], ["This field is required."])

    def test_location_name_empty(self):
        form = forms.LocationNameForm(data={})

        self.assertEqual(form.errors["name"], ["This field is required."])

    def test_location_address_address_field_empty(self):
        form = forms.LocationAddressForm(data={"address": ""})

        self.assertEqual(form.errors["address"], ["This field is required."])

    def test_location_address_city_field_empty(self):
        form = forms.LocationAddressForm(data={"city": ""})

        self.assertEqual(form.errors["city"], ["This field is required."])

    def test_location_address_province_field_empty(self):
        form = forms.LocationAddressForm(data={"province": ""})

        self.assertEqual(form.errors["province"], ["This field is required."])

    def test_location_address_postal_field_empty(self):
        form = forms.LocationAddressForm(data={"postal_code": ""})

        self.assertEqual(form.errors["postal_code"], ["This field is required."])

    def test_location_contact_email_empty(self):
        form = forms.LocationContactForm(data={"contact_email": ""})

        self.assertEqual(form.errors["contact_email"], ["This field is required."])

    def test_location_contact_email_format(self):
        form = forms.LocationContactForm(data={"contact_email": "notanemail"})

        self.assertEqual(form.errors["contact_email"], ["Enter a valid email address."])

    def test_location_contact_phone_empty(self):
        form = forms.LocationContactForm(data={"contact_phone": ""})

        self.assertEqual(form.errors["contact_phone"], ["This field is required."])

    def test_location_contact_phone_format(self):
        form = forms.LocationContactForm(data={"contact_phone": "notaphonenumber"})

        self.assertEqual(
            form.errors["contact_phone"],
            ["Enter a valid phone number (e.g. +12125552368)."],
        )


class LocationModel(TestCase):
    def test_location_model_generates_short_code_on_save(self):
        location = Location.objects.create(
            category="category",
            name="Name of venue",
            address="Address line 1",
            city="Ottawa",
            province="ON",
            postal_code="K1K 1K1",
            contact_email="test@test.com",
            contact_phone="613-555-5555",
        )

        self.assertNotEqual(location.short_code, "")
        self.assertEqual(len(location.short_code), 8)
        self.assertTrue(location.short_code.isalnum)


# Generate signing key for following tests
signing_key = utils.generate_signature_key()


@override_settings(QRCODE_SIGNATURE_PRIVATE_KEY=signing_key)
class Utils(TestCase):
    def test_generate_short_code_default_length(self):
        code = utils.generate_random_key()
        self.assertEqual(len(code), 8)

    def test_generate_short_code_custom_length(self):
        code = utils.generate_random_key(5)
        self.assertEqual(len(code), 5)

    def test_generate_short_code_alphanumeric(self):
        code = utils.generate_random_key()
        self.assertTrue(code.isalnum())

    def test_generate_payload(self):
        location = Location.objects.create(
            category="category",
            name="Name of venue",
            address="Address line 1",
            city="Ottawa",
            province="ON",
            postal_code="K1K 1K1",
            contact_email="test@test.com",
            contact_phone="613-555-5555",
        )

        payload = utils.generate_payload(location)
        self.assertIn(location.short_code, payload)
        self.assertIn(location.name, payload)
        self.assertIn(location.address, payload)
        self.assertIn(location.city, payload)

    def test_sign_payload(self):
        location = Location.objects.create(
            category="category",
            name="Name of venue",
            address="Address line 1",
            city="Ottawa",
            province="ON",
            postal_code="K1K 1K1",
            contact_email="test@test.com",
            contact_phone="613-555-5555",
        )

        payload = utils.generate_payload(location)
        signed = utils.sign_payload(payload)
        
        # Is the payload base64 encoded?
        self.assertTrue(is_base64(signed))

        # Extract the verify key from the signature key
        signature_key = utils.load_signature_key()
        verify_key = signature_key.verify_key

        # Verify the signed payload with the verify key
        verify_key.verify(signed.encode(), encoder=Base64Encoder)

    def test_generate_qr_code(self):
        url = "http://thisisjustatesturl.com/#thiswouldbethesignedpayload"

        qrcode = utils.generate_qrcode(url)
        self.assertTrue(is_svg(qrcode))

    def test_get_signed_qrcode(self):
        location = Location.objects.create(
            category="category",
            name="Name of venue",
            address="Address line 1",
            city="Ottawa",
            province="ON",
            postal_code="K1K 1K1",
            contact_email="test@test.com",
            contact_phone="613-555-5555",
        )

        qrcode = utils.get_signed_qrcode(location)
        self.assertTrue(is_svg(qrcode))

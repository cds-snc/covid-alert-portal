from django.test import TestCase
from django.urls import reverse

from waffle.models import Switch

from . import forms
from .models import Registrant, Location
from .utils import generate_random_key


class RegisterView(TestCase):
    def setUp(self):
        pass

    def test_start_page(self):
        response = self.client.get(reverse("register:start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Create a COVID Alert QR code for your venue</h1>",
            html=True,
        )

    def test_email_page(self):
        response = self.client.get(reverse("register:registrant_email"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Where should we send your poster?</h1>",
            html=True,
        )

    def test_name_page(self):
        r = Registrant.objects.create(email="test@test.com")

        response = self.client.get(
            reverse("register:registrant_name", kwargs={"pk": r.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>What is your name?</h1>",
            html=True,
        )

    def test_confirmation_page(self):
        email = "test@test.com"

        # add email to session
        session = self.client.session
        session["registrant_email"] = email
        session.save()

        r = Registrant.objects.create(email=email)

        response = self.client.get(
            reverse("register:confirmation", kwargs={"pk": r.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<h1>Your request for a poster has been submitted</h1>",
            html=True,
        )
        self.assertContains(
            response,
            'Thank you. As soon as it’s ready, your poster will be emailed to <a href="mailto:{0}">{0}</a>'.format(
                email
            ),
        )


class RegisterLocationDetails(TestCase):
    def setUp(self):
        Switch.objects.create(name="QR_CODES", active=True)

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


class Utils(TestCase):
    def test_generate_short_code_default_length(self):
        code = generate_random_key()
        self.assertEqual(len(code), 8)

    def test_generate_short_code_custom_length(self):
        code = generate_random_key(5)
        self.assertEqual(len(code), 5)

    def test_generate_short_code_alphanumeric(self):
        code = generate_random_key()
        self.assertTrue(code.isalnum())

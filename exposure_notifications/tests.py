from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from profiles.tests import AdminUserTestCase, get_other_credentials
from register.models import Location
from datetime import datetime, timezone
from .models import Notification
from .forms import DateForm, SeverityForm

User = get_user_model()


class NotificationsTestCase(AdminUserTestCase):
    def setUp(self):
        super().setUp()

        # Authorize the default user to perform alerts
        user = User.objects.get(name="testuser")
        user.user_permissions.add(Permission.objects.get(codename="can_send_alerts"))

        # Populate test data
        location1 = Location.objects.create(
            category="Restaurant",
            name="Nandos",
            address="123 main street",
            city="Winnipeg",
            province="MB",
            postal_code="ABC 123",
            contact_email="abc@cds-snc.ca",
            contact_phone="6136666666",
        )
        location2 = Location.objects.create(
            category="Restaurant",
            name="Bobs",
            address="123 main street",
            city="Winnipeg",
            province="MB",
            postal_code="ABC 123",
            contact_email="abc@cds-snc.ca",
            contact_phone="6136666666",
        )
        Location.objects.create(
            category="Restaurant",
            name="Bobs",
            address="123 main street",
            city="Winnipeg",
            province="ON",
            postal_code="ABC 123",
            contact_email="abc@cds-snc.ca",
            contact_phone="6136666666",
        )
        now = datetime.now(timezone.utc)
        Notification.objects.create(
            severity=1,
            start_date=now,
            end_date=now,
            created_date=now,
            created_by=User.objects.get(name="testuser"),
            location=location1,
        )
        Notification.objects.create(
            severity=1,
            start_date=now,
            end_date=now,
            created_date=now,
            created_by=User.objects.get(name="testuser"),
            location=location2,
        )


class SearchView(NotificationsTestCase):
    def test_permissions(self):
        # Ensure that a user with no permissions cannot access this end point
        credentials = get_other_credentials()
        User.objects.create(**credentials)
        self.login(credentials)
        response = self.client.get(reverse("exposure_notifications:start"))
        self.assertEqual(response.status_code, 302)

    def test_initial_view(self):
        # Assert that the correct template is loaded and there are no search results initially
        self.login()
        response = self.client.get(reverse("exposure_notifications:start"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")

        # assert that there are no locations listed
        self.assertEqual(len(response.context["object_list"]), 0)

    def test_post_request(self):
        # Test that posting the form will redirect back to the same page, but with query params
        self.login()
        response = self.client.post(
            reverse("exposure_notifications:start"), {"search_text": "nandos"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("exposure_notifications:start") + "?search_text=nandos",
        )

    def test_search_functionality(self):
        # Test that GET with a query param produces search results
        self.login()
        response = self.client.get(
            reverse("exposure_notifications:start"), {"search_text": "nandos"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")

        # assert that there is a search result found
        self.assertEqual(len(response.context["object_list"]), 1)

    def test_province_filter(self):
        # Test that searching for 'bobs' will only produce one result because the other is in a different province
        self.login()
        response = self.client.get(
            reverse("exposure_notifications:start"), {"search_text": "bobs"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")

        # assert that there is a search result found
        self.assertEqual(len(response.context["object_list"]), 1)

    def test_superadmin_no_province_filter(self):
        # Test that searching for 'bobs' will only produce both results for super admins
        credentials = get_other_credentials(is_superuser=True)
        User.objects.create_superuser(**credentials)
        self.login(credentials)
        response = self.client.get(
            reverse("exposure_notifications:start"), {"search_text": "bobs"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")

        # assert that there is a search result found
        self.assertEqual(len(response.context["object_list"]), 2)


class ProfileView(NotificationsTestCase):
    def test_profile_view(self):
        # Ensure that the profile view is rendered correctly
        self.login()
        location = Location.objects.get(name="Nandos")
        response = self.client.get(
            reverse("exposure_notifications:profile", args=[location.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")


class DatetimeView(NotificationsTestCase):
    def test_datetime_view_no_location(self):
        # Ensure that the datetime view is not accessible if there is no location cached in the session
        self.login()
        response = self.client.get(reverse("exposure_notifications:datetime"))
        self.assertEqual(response.status_code, 302)

    def test_datetime_view(self):
        # Ensure that the datetime view is rendered correctly with a cached location
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("exposure_notifications:profile", args=[location.id]))
        response = self.client.get(reverse("exposure_notifications:datetime"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "datetime.html")

    def test_invalid_data(self):
        # Ensure that the datetime form handles data errors
        self.assertTrue(DateForm({"day": 1, "month": 2, "year": 2021}).is_valid())
        self.assertFalse(DateForm({"day": 1, "year": 2021}).is_valid())
        self.assertFalse(DateForm({"day": 1, "month": 2, "year": 2020}).is_valid())
        self.assertFalse(DateForm({"day": 1, "month": 2}).is_valid())
        self.assertFalse(DateForm({"month": 2, "year": 2021}).is_valid())
        self.assertFalse(DateForm({"day": 0, "month": 2, "year": 2021}).is_valid())
        self.assertFalse(DateForm({"day": 32, "month": 2, "year": 2021}).is_valid())
        self.assertFalse(DateForm({"day": 1, "month": 13, "year": 2021}).is_valid())


class SeverityView(NotificationsTestCase):
    def test_severity_view_no_cache(self):
        # Ensure that the severity view is not accessible if there is no location/datetime cached in the session
        self.login()
        response = self.client.get(reverse("exposure_notifications:severity"))
        self.assertEqual(response.status_code, 302)

    def test_severity_view(self):
        # Ensure that the severity view is rendered correctly with previously cached data
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("exposure_notifications:profile", args=[location.id]))
        self.client.post(
            reverse("exposure_notifications:datetime"),
            {"day": 1, "month": 1, "year": 2021},
        )
        response = self.client.get(reverse("exposure_notifications:severity"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "severity.html")

    def test_invalid_data(self):
        # Ensure that the severity form handles data errors
        self.assertTrue(SeverityForm({"alert_level": 1}).is_valid())
        self.assertFalse(SeverityForm({"alert_level": 0}).is_valid())
        self.assertFalse(SeverityForm({"alert_level": 4}).is_valid())
        self.assertFalse(SeverityForm({}).is_valid())


class ConfirmView(NotificationsTestCase):
    def test_confirm_view_no_cache(self):
        # Ensure that the confirm view is not accessible if there is no location/datetime/severity cached in the session
        self.login()
        response = self.client.get(reverse("exposure_notifications:confirm"))
        self.assertEqual(response.status_code, 302)

    def test_confirm_view(self):
        # Ensure that the confirm view is rendered correctly with previously cached data
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("exposure_notifications:profile", args=[location.id]))
        self.client.post(
            reverse("exposure_notifications:datetime"),
            {"day": 1, "month": 1, "year": 2021},
        )
        self.client.post(reverse("exposure_notifications:severity"), {"alert_level": 1})
        response = self.client.get(reverse("exposure_notifications:confirm"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "confirm.html")

    def test_notification_not_creation(self):
        # Ensure that no notifications are created if we don't have cached data
        self.login()
        response = self.client.post(reverse("exposure_notifications:confirm"), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("exposure_notifications:start"))

    def test_notification_creation(self):
        # Ensure that a notificatioon can successfully be created
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("exposure_notifications:profile", args=[location.id]))
        self.client.post(
            reverse("exposure_notifications:datetime"),
            {"day": 1, "month": 1, "year": 2021},
        )
        self.client.post(reverse("exposure_notifications:severity"), {"alert_level": 1})
        response = self.client.post(reverse("exposure_notifications:confirm"), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("exposure_notifications:confirmed"))
        notifications = Notification.objects.all()
        self.assertEqual(len(notifications), 3)


class ConfirmedView(NotificationsTestCase):
    def test_confirmed_view_no_cache(self):
        # Ensure that the confirmed view is not accessible if there is no location/datetime/severity cached in the session
        self.login()
        response = self.client.get(reverse("exposure_notifications:confirmed"))
        self.assertEqual(response.status_code, 302)

    def test_confirmed_view(self):
        # Ensure that the confirmed view is rendered correctly with previously cached data
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("exposure_notifications:profile", args=[location.id]))
        self.client.post(
            reverse("exposure_notifications:datetime"),
            {"day": 1, "month": 1, "year": 2021},
        )
        self.client.post(reverse("exposure_notifications:severity"), {"alert_level": 1})
        response = self.client.get(reverse("exposure_notifications:confirmed"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "confirmed.html")


class HistoryView(NotificationsTestCase):
    def test_initial_view(self):
        # Assert that the correct template is loaded and that all results are visible
        self.login()
        response = self.client.get(reverse("exposure_notifications:history"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "history.html")

        # assert that there all notifications are listed
        self.assertEqual(len(response.context["object_list"]), 2)

    def test_post_request(self):
        # Test that posting the form will redirect back to the same page, but with query params
        self.login()
        response = self.client.post(
            reverse("exposure_notifications:history"), {"search_text": "nandos"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("exposure_notifications:history") + "?search_text=nandos",
        )

    def test_search_functionality(self):
        # Test that GET with a query param produces search results
        self.login()
        response = self.client.get(
            reverse("exposure_notifications:history"), {"search_text": "nandos"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "history.html")

        # assert that there is a search result found
        self.assertEqual(len(response.context["object_list"]), 1)


class DetailsView(NotificationsTestCase):
    def test_details_view(self):
        # Ensure that the details view is rendered correctly
        self.login()
        notification = Notification.objects.get(location__name="Nandos")
        response = self.client.get(
            reverse("exposure_notifications:details", args=[notification.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "details.html")

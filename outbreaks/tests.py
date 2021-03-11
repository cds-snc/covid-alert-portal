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
            category="restaurant_bar_coffee",
            name="Nandos",
            address="123 main street",
            city="Winnipeg",
            province="MB",
            postal_code="ABC 123",
            contact_email="abc@cds-snc.ca",
            contact_phone="6136666666",
        )
        location2 = Location.objects.create(
            category="restaurant_bar_coffee",
            name="Bobs",
            address="123 main street",
            city="Winnipeg",
            province="MB",
            postal_code="ABC 123",
            contact_email="abc@cds-snc.ca",
            contact_phone="6136666666",
        )
        Location.objects.create(
            category="restaurant_bar_coffee",
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
        response = self.client.get(reverse("outbreaks:search"))
        self.assertEqual(response.status_code, 302)

    def test_initial_view(self):
        # Assert that the correct template is loaded and there are no search results initially
        self.login()
        response = self.client.get(reverse("outbreaks:search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")

        # assert that there are no locations listed
        self.assertEqual(len(response.context["object_list"]), 0)

    def test_search_functionality(self):
        # Test that GET with a query param produces search results
        self.login()
        response = self.client.get(
            reverse("outbreaks:search"), {"search_text": "nandos"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")

        # assert that there is a search result found
        self.assertEqual(len(response.context["object_list"]), 1)

    def test_province_filter(self):
        # Test that searching for 'bobs' will only produce one result because the other is in a different province
        self.login()
        response = self.client.get(reverse("outbreaks:search"), {"search_text": "bobs"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")

        # assert that there is a search result found
        self.assertEqual(len(response.context["object_list"]), 1)

    def test_superadmin_no_province_filter(self):
        # Test that searching for 'bobs' will only produce both results for super admins
        credentials = get_other_credentials(is_superuser=True)
        User.objects.create_superuser(**credentials)
        self.login(credentials)
        response = self.client.get(reverse("outbreaks:search"), {"search_text": "bobs"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")

        # assert that there is a search result found
        self.assertEqual(len(response.context["object_list"]), 2)


class ProfileView(NotificationsTestCase):
    def test_profile_view(self):
        # Ensure that the profile view is rendered correctly
        self.login()
        location = Location.objects.get(name="Nandos")
        response = self.client.get(reverse("outbreaks:profile", args=[location.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")


class DatetimeView(NotificationsTestCase):
    def test_datetime_view_no_location(self):
        # Ensure that the datetime view is not accessible if there is no location cached in the session
        self.login()
        response = self.client.get(reverse("outbreaks:datetime"))
        self.assertEqual(response.status_code, 302)

    def test_datetime_view(self):
        # Ensure that the datetime view is rendered correctly with a cached location
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("outbreaks:profile", args=[location.id]))
        response = self.client.get(reverse("outbreaks:datetime"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "datetime.html")

    def test_invalid_data(self):
        # Ensure that the datetime form handles data errors
        self.assertTrue(
            DateForm(1, {"day_0": 1, "month_0": 2, "year_0": 2021}).is_valid()
        )
        self.assertFalse(DateForm(1, {"day_0": 1, "year_0": 2021}).is_valid())
        self.assertFalse(
            DateForm(1, {"day_0": 1, "month_0": 2, "year_0": 2020}).is_valid()
        )
        self.assertFalse(DateForm(1, {"day_0": 1, "month_0": 2}).is_valid())
        self.assertFalse(DateForm(1, {"month_0": 2, "year_0": 2021}).is_valid())
        self.assertFalse(
            DateForm(1, {"day_0": 0, "month_0": 2, "year_0": 2021}).is_valid()
        )
        self.assertFalse(
            DateForm(1, {"day_0": 32, "month_0": 2, "year_0": 2021}).is_valid()
        )
        self.assertFalse(
            DateForm(1, {"day_0": 1, "month_0": 13, "year_0": 2021}).is_valid()
        )

    def test_add_remove_date(self):
        """
        Assert that adding/removing a new date will lead us back to the same page, but with new form fields
        """

        # Login and ensure that a location has been cached
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("outbreaks:profile", args=[location.id]))

        # Post an 'add date' request and ensure it redirects back to the same page
        response = self.client.post(
            reverse("outbreaks:datetime"), {"adjust_dates": "add"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("outbreaks:datetime")))

        # Assert that getting the same page now returns two dates
        response = self.client.get(reverse("outbreaks:datetime"))
        self.assertContains(response, "day_0")
        self.assertContains(response, "day_1")

        # Post a 'remove date' request and ensure it redirects back to the same page
        response = self.client.post(
            reverse("outbreaks:datetime"), {"adjust_dates": "remove"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("outbreaks:datetime")))

        # Assert that getting the same page now returns a single date
        response = self.client.get(reverse("outbreaks:datetime"))
        self.assertContains(response, "day_0")
        self.assertNotContains(response, "day_1")

    def test_duplicate_error(self):
        """
        Assert that setting the datetime to a duplicate raises an error
        """

        # Login and ensure that a location has been cached
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("outbreaks:profile", args=[location.id]))

        # Post a date
        self.client.post(
            reverse("outbreaks:datetime"), {"day_0": 1, "month_0": 1, "year_0": 2021}
        )
        self.client.post(reverse("outbreaks:severity"), {"alert_level": 1})
        response = self.client.post(reverse("outbreaks:confirm"), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("outbreaks:confirmed"))

        # Post duplicate date
        response = self.client.post(
            reverse("outbreaks:datetime"), {"day_0": 1, "month_0": 1, "year_0": 2021}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "datetime.html")
        self.assertContains(response, "error")


class SeverityView(NotificationsTestCase):
    def test_severity_view_no_cache(self):
        # Ensure that the severity view is not accessible if there is no location/datetime cached in the session
        self.login()
        response = self.client.get(reverse("outbreaks:severity"))
        self.assertEqual(response.status_code, 302)

    def test_severity_view(self):
        # Ensure that the severity view is rendered correctly with previously cached data
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("outbreaks:profile", args=[location.id]))
        self.client.post(
            reverse("outbreaks:datetime"),
            {"day_0": 1, "month_0": 1, "year_0": 2021},
        )
        response = self.client.get(reverse("outbreaks:severity"))
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
        response = self.client.get(reverse("outbreaks:confirm"))
        self.assertEqual(response.status_code, 302)

    def test_confirm_view(self):
        # Ensure that the confirm view is rendered correctly with previously cached data
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("outbreaks:profile", args=[location.id]))
        self.client.post(
            reverse("outbreaks:datetime"),
            {"day_0": 1, "month_0": 1, "year_0": 2021},
        )
        self.client.post(reverse("outbreaks:severity"), {"alert_level": 1})
        response = self.client.get(reverse("outbreaks:confirm"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "confirm.html")

    def test_notification_not_creation(self):
        # Ensure that no notifications are created if we don't have cached data
        self.login()
        response = self.client.post(reverse("outbreaks:confirm"), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("outbreaks:search"))

    def test_notification_creation(self):
        # Ensure that a notificatioon can successfully be created
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("outbreaks:profile", args=[location.id]))
        self.client.post(
            reverse("outbreaks:datetime"),
            {"day_0": 1, "month_0": 1, "year_0": 2021},
        )
        self.client.post(reverse("outbreaks:severity"), {"alert_level": 1})
        response = self.client.post(reverse("outbreaks:confirm"), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("outbreaks:confirmed"))
        notifications = Notification.objects.all()
        self.assertEqual(len(notifications), 3)


class ConfirmedView(NotificationsTestCase):
    def test_confirmed_view_no_cache(self):
        # Ensure that the confirmed view is not accessible if there is no location/datetime/severity cached in the session
        self.login()
        response = self.client.get(reverse("outbreaks:confirmed"))
        self.assertEqual(response.status_code, 302)

    def test_confirmed_view(self):
        # Ensure that the confirmed view is rendered correctly with previously cached data
        self.login()
        location = Location.objects.get(name="Nandos")
        self.client.get(reverse("outbreaks:profile", args=[location.id]))
        self.client.post(
            reverse("outbreaks:datetime"),
            {"day_0": 1, "month_0": 1, "year_0": 2021},
        )
        self.client.post(reverse("outbreaks:severity"), {"alert_level": 1})
        response = self.client.get(reverse("outbreaks:confirmed"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "confirmed.html")


class HistoryView(NotificationsTestCase):
    def test_initial_view_redirect(self):
        # Ensure that the initial view redirects to add sort params
        self.login()
        response = self.client.get(reverse("outbreaks:history"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("outbreaks:history")))

    def test_initial_view_all_results(self):
        # Assert that the correct template is loaded and that all results are visible
        self.login()
        response = self.client.get(
            reverse("outbreaks:history"), {"sort": "name", "order": "asc"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "history.html")

        # assert that there all notifications are listed
        self.assertEqual(len(response.context["object_list"]), 2)

    def test_search_functionality(self):
        # Test that GET with a query param produces search results
        self.login()
        response = self.client.get(
            reverse("outbreaks:history"),
            {"search_text": "nandos", "sort": "name", "order": "asc"},
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
        response = self.client.get(reverse("outbreaks:details", args=[notification.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "details.html")

from django.test import TestCase

from django.urls import reverse
from django.contrib.auth import get_user_model


class HomePageView(TestCase):
    def test_start(self):
        """
        Just see the start page
        """
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Welcome to the logged out homepage")


class RestristedPageViews(TestCase):
    #  These should redirect us
    def test_code(self):
        response = self.client.get(reverse('code'))
        self.assertRedirects(response, '/login/?next=/code/')

    def test_start(self):
        response = self.client.get(reverse('start'))
        self.assertRedirects(response, '/login/?next=/start/')


class AuthenticatedView(TestCase):
    def setUp(self):
        self.credentials = {
            'email': 'test@test.com',
            'name': 'testuser',
            'password': 'testpassword'}
        User = get_user_model()
        User.objects.create_user(**self.credentials)
        self.credentials['username'] = 'test@test.com'  # Because username is what is posted to the login page, even if email is the username field we need to add it here. Adding it before creates an error since it's not expected as part of create_user()

    def test_loginpage(self):
        #  Get the login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")

        #  Test logging in
        response = self.client.post('/login/', self.credentials, follow=True)
        print(response.context['user'])
        self.assertTrue(response.context['user'].is_active)

    def test_code(self):
        """
        Just see the code page and one code
        """
        user_model = get_user_model()
        self.client.login(username='test@test.com', password='testpassword')
        response = self.client.get(reverse('code'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Provide patient with code")
        self.assertContains(response,
                            "<code id=\"big-code\">{}</code>".format(response.context['code']))

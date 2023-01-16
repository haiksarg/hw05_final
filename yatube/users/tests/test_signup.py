from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class SignupFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_form(self):
        response = self.guest_client.post(reverse('users:signup'), {
            'first_name': 'testname',
            'last_name': 'testname',
            'username': 'testuser',
            'email': 'test@email.com',
            'password1': 'GtaanGOO202_',
            'password2': 'GtaanGOO202_',
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.last()
        self.assertIsNotNone(new_user)

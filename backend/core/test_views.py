from django.test import TestCase, Client
from django.urls import reverse
from .models import *
from account.models import User

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.home = reverse("home")
        self.credentials = {
            'username': 'arash1',
            'email': 'arash1@example.com',
            'password': 'arash1'}
        self.user = User.objects.create_user(**self.credentials)

    def test_home_redirects_when_logged_out(self):
        response = self.client.get(self.home)
        self.assertEqual(response.status_code, 302)

    def test_home_GET_when_logged_in(self):
        self.client.login(username='arash1', password='arash1')
        response = self.client.get(self.home)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')

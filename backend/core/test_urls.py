from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .views import *


class test_core_url_resolves(SimpleTestCase):
    def test_home_url_resolves(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, home)

    def test_post_url_resolves(self):
        url = reverse('post', args=['some_str'])
        self.assertEqual(resolve(url).func, post)

    def test_like_url_resolves(self):
        url = reverse('like')
        self.assertEqual(resolve(url).func, like)

    def test_delete_url_resolves(self):
        url = reverse('delete', args=['some_str'])
        self.assertEqual(resolve(url).func, deletepost)

    def test_search_url_resolves(self):
        url = reverse('search')
        self.assertEqual(resolve(url).func, search)

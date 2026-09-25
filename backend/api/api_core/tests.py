import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from account.models import User
from core.models import Post, Comment


MEDIA_ROOT = tempfile.mkdtemp()


def make_image(name='test.png'):
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, 'PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostAPITests(APITestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user  = User.objects.create_user(username='arash1', email='arash1@example.com', password='Str0ng-pass!')
        self.other = User.objects.create_user(username='sara', email='sara@example.com', password='Str0ng-pass!')
        self.post  = Post.objects.create_post(user=self.other, image=make_image(), caption='hi')
        self.client.force_authenticate(self.user)

    def test_requires_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(reverse('api_post-list')).status_code, 401)

    def test_create_post(self):
        response = self.client.post(reverse('api_post-list'), {'image': make_image(), 'caption': 'new'}, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'arash1')

    def test_list_and_detail(self):
        response = self.client.get(reverse('api_post-list'))
        self.assertEqual(response.data['count'], 1)
        detail = self.client.get(reverse('api_post-detail', args=[self.post.id]))
        self.assertEqual(detail.data['caption'], 'hi')

    def test_only_owner_can_edit_or_delete(self):
        url = reverse('api_post-detail', args=[self.post.id])
        self.assertEqual(self.client.patch(url, {'caption': 'x'}).status_code, 403)
        self.assertEqual(self.client.delete(url).status_code, 403)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(url, {'caption': 'x'}).status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)

    def test_like_and_unlike(self):
        url = reverse('api_post-like', args=[self.post.id])
        response = self.client.post(url)
        self.assertEqual((response.data['is_liked'], response.data['likes_count']), (True, 1))
        response = self.client.delete(url)
        self.assertEqual((response.data['is_liked'], response.data['likes_count']), (False, 0))

    def test_feed_only_shows_followed_users(self):
        feed = reverse('api_post-feed')
        self.assertEqual(self.client.get(feed).data['count'], 0)
        self.user.follow(self.other)
        self.assertEqual(self.client.get(feed).data['count'], 1)

    def test_comments(self):
        url = reverse('api_post_comments', args=[self.post.id])
        response = self.client.post(url, {'text': 'nice'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.get(url).data['count'], 1)

        comment_url = reverse('api_comment_detail', args=[response.data['id']])
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(comment_url).status_code, 403)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(comment_url).status_code, 204)
        self.assertFalse(Comment.objects.exists())

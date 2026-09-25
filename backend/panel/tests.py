import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from account.models import User
from core.models import Comment, Post

MEDIA_ROOT = tempfile.mkdtemp()


def make_image():
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, 'PNG')
    return SimpleUploadedFile('p.png', buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PanelTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.admin = User.objects.create_superuser(username='boss', email='boss@example.com', password='Str0ng-pass!')
        self.mod = User.objects.create_user(username='mod', email='mod@example.com', password='Str0ng-pass!', is_staff=True)
        self.member = User.objects.create_user(username='sara', email='sara@example.com', password='Str0ng-pass!')
        self.post = Post.objects.create_post(user=self.member, image=make_image(), caption='hello snakes')
        self.comment = Comment.objects.create_comment(post=self.post, user=self.member, text='first!')

    def test_login_required_and_staff_only(self):
        url = reverse('panel:dashboard')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.member)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_every_page_renders_for_staff(self):
        self.client.force_login(self.mod)
        for url in (reverse('panel:dashboard'), reverse('panel:users'), reverse('panel:posts'),
                    reverse('panel:comments'), reverse('panel:user-detail', args=[self.member.pk])):
            self.assertEqual(self.client.get(url).status_code, 200, url)
        response = self.client.get(reverse('panel:dashboard'))
        self.assertEqual((response.context['user_count'], response.context['post_count']), (3, 1))

    def test_search(self):
        self.client.force_login(self.mod)
        response = self.client.get(reverse('panel:users'), {'q': 'sar'})
        self.assertEqual([u.username for u in response.context['users']], ['sara'])
        response = self.client.get(reverse('panel:posts'), {'q': 'snakes'})
        self.assertEqual(len(response.context['posts']), 1)

    def test_block_rules(self):
        self.client.force_login(self.mod)
        self.client.post(reverse('panel:user-toggle-active', args=[self.member.pk]))
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)
        # a plain staff member can't block the superuser, nor themselves
        self.client.post(reverse('panel:user-toggle-active', args=[self.admin.pk]))
        self.client.post(reverse('panel:user-toggle-active', args=[self.mod.pk]))
        self.admin.refresh_from_db(); self.mod.refresh_from_db()
        self.assertTrue(self.admin.is_active and self.mod.is_active)

    def test_only_superuser_changes_staff(self):
        url = reverse('panel:user-toggle-staff', args=[self.member.pk])
        self.client.force_login(self.mod)
        self.client.post(url)
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_staff)
        self.client.force_login(self.admin)
        self.client.post(url)
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_staff)

    def test_moderation_deletes(self):
        self.client.force_login(self.mod)
        self.client.post(reverse('panel:comment-delete', args=[self.comment.pk]))
        self.assertFalse(Comment.objects.exists())
        self.client.post(reverse('panel:post-delete', args=[self.post.pk]), {'next': 'https://evil.example/'})
        self.assertFalse(Post.objects.exists())

    def test_get_cannot_delete(self):
        self.client.force_login(self.mod)
        self.assertEqual(self.client.get(reverse('panel:post-delete', args=[self.post.pk])).status_code, 405)

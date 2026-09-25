import re
import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from account.cache import stats_key
from account.models import User
from core.models import Comment, Post

MEDIA_ROOT = tempfile.mkdtemp()


def make_image():
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, 'PNG')
    return SimpleUploadedFile('p.png', buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class WebFeatureTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='arash', email='arash@example.com', password='Str0ng-pass!')
        self.other = User.objects.create_user(username='sara', email='sara@example.com', password='Str0ng-pass!')
        self.stranger = User.objects.create_user(username='nima', email='nima@example.com', password='Str0ng-pass!')
        self.post = Post.objects.create_post(user=self.other, image=make_image(), caption='hi')
        self.client.force_login(self.user)

    # --- feed tabs ----------------------------------------------------------

    def test_following_tab_only_shows_followed_users(self):
        Post.objects.create_post(user=self.stranger, image=make_image(), caption='x')
        self.assertEqual(len(self.client.get(reverse('home')).context['posts']), 2)
        self.assertEqual(len(self.client.get(reverse('home'), {'tab': 'following'}).context['posts']), 0)
        self.user.follow(self.other)
        posts = self.client.get(reverse('home'), {'tab': 'following'}).context['posts']
        self.assertEqual([p.caption for p, _ in posts], ['hi'])

    # --- like / follow / delete are POST-only ------------------------------

    def test_like_requires_post(self):
        url = reverse('like')
        self.assertEqual(self.client.get(url, {'post_id': self.post.id}).status_code, 405)
        self.client.post(url, {'post_id': self.post.id, 'next': '/'})
        self.assertTrue(self.post.is_liked_by(self.user))

    def test_next_cannot_leave_the_site(self):
        response = self.client.post(reverse('like'), {'post_id': self.post.id, 'next': 'https://evil.example/'})
        self.assertEqual(response.url, '/')

    def test_follow_via_post_and_follow_lists(self):
        self.assertEqual(self.client.get(reverse('follow'), {'username': 'sara'}).status_code, 405)
        self.client.post(reverse('follow'), {'username': 'sara', 'next': '/'})
        self.assertTrue(self.user.is_following(self.other))
        response = self.client.get(reverse('followers', args=['sara']))
        self.assertEqual(list(response.context['people']), [self.user])
        response = self.client.get(reverse('following', args=['arash']))
        self.assertEqual(list(response.context['people']), [self.other])

    def test_delete_post_requires_post(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('delete', args=[self.post.id])).status_code, 405)
        self.client.post(reverse('delete', args=[self.post.id]))
        self.assertFalse(Post.objects.exists())

    # --- comments -----------------------------------------------------------

    def test_add_and_list_comments(self):
        response = self.client.post(reverse('post_comments', args=[self.post.id]), {'text': 'nice'}, follow=True)
        self.assertContains(response, 'nice')
        self.assertEqual(list(response.context['comments'].values_list('text', flat=True)), ['nice'])

    def test_empty_comment_rejected(self):
        self.client.post(reverse('post_comments', args=[self.post.id]), {'text': '   '})
        self.assertFalse(Comment.objects.exists())

    def test_comment_delete_permissions(self):
        comment = Comment.objects.create_comment(post=self.post, user=self.user, text='mine')
        url = reverse('delete_comment', args=[comment.id])
        self.client.force_login(self.stranger)
        self.client.post(url)
        self.assertTrue(Comment.objects.exists())
        # the post owner may remove comments on their post
        self.client.force_login(self.other)
        self.client.post(url)
        self.assertFalse(Comment.objects.exists())

    # --- password reset -----------------------------------------------------

    def test_password_reset_flow(self):
        self.client.logout()
        response = self.client.post(reverse('password_reset'), {'email': 'arash@example.com'})
        self.assertRedirects(response, reverse('password_reset_done'))
        link = re.search(r'/account/password-reset/[^/\s]+/[^/\s]+/', mail.outbox[0].body).group(0)
        response = self.client.get(link, follow=True)
        self.assertTrue(response.context['validlink'])
        response = self.client.post(response.redirect_chain[-1][0],
                                    {'new_password1': 'Reset-pass-9!', 'new_password2': 'Reset-pass-9!'})
        self.assertRedirects(response, reverse('password_reset_complete'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Reset-pass-9!'))

    def test_login_page_links_to_reset(self):
        self.client.logout()
        self.assertContains(self.client.get(reverse('login')), reverse('password_reset'))

    # --- caching ------------------------------------------------------------

    def test_profile_counters_are_cached_and_invalidated(self):
        self.assertEqual(self.other.followers_count, 0)
        self.assertIsNotNone(cache.get(stats_key(self.other.pk)))
        self.user.follow(self.other)
        self.assertIsNone(cache.get(stats_key(self.other.pk)))  # dropped by the signal
        self.assertEqual(self.other.followers_count, 1)
        Post.objects.create_post(user=self.other, image=make_image())
        self.assertEqual(self.other.posts_count, 2)

    def test_suggestions_drop_someone_once_followed(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'href="/account/profile/sara/" class="suggest"')
        self.user.follow(self.other)
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'href="/account/profile/sara/" class="suggest"')

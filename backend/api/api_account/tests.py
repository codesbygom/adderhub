from django.urls import reverse
from rest_framework.test import APITestCase
from account.models import User


class AccountAPITests(APITestCase):

    def setUp(self):
        self.user  = User.objects.create_user(username='arash1', email='arash1@example.com', password='Str0ng-pass!')
        self.other = User.objects.create_user(username='sara', email='sara@example.com', password='Str0ng-pass!')

    def test_signup_hashes_password_and_hides_it(self):
        response = self.client.post(reverse('api_signup'), {
            'username': 'newbie', 'email': 'newbie@example.com', 'password': 'An0ther-pass!'})
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        self.assertTrue(User.objects.get(username='newbie').check_password('An0ther-pass!'))

    def test_signup_rejects_weak_password(self):
        response = self.client.post(reverse('api_signup'), {
            'username': 'weak', 'email': 'weak@example.com', 'password': '123'})
        self.assertEqual(response.status_code, 400)

    def test_login_returns_tokens(self):
        response = self.client.post(reverse('token_obtain'), {'username': 'arash1', 'password': 'Str0ng-pass!'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get(reverse('api_me')).status_code, 401)
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('api_me'))
        self.assertEqual(response.data['email'], 'arash1@example.com')

    def test_public_profile_hides_email(self):
        response = self.client.get(reverse('api_user_detail', args=[self.other.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('email', response.data)

    def test_user_search(self):
        response = self.client.get(reverse('api_user_list'), {'search': 'sar'})
        self.assertEqual([u['username'] for u in response.data['results']], ['sara'])

    def test_update_profile(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(reverse('api_update'), {'bio': 'hello'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, 'hello')

    def test_change_password(self):
        self.client.force_authenticate(self.user)
        url = reverse('api_change_password')
        bad = self.client.put(url, {'old_password': 'wrong', 'new_password': 'N3w-pass-ok!', 'confirm_new_password': 'N3w-pass-ok!'})
        self.assertEqual(bad.status_code, 400)
        ok = self.client.put(url, {'old_password': 'Str0ng-pass!', 'new_password': 'N3w-pass-ok!', 'confirm_new_password': 'N3w-pass-ok!'})
        self.assertEqual(ok.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('N3w-pass-ok!'))

    def test_follow_and_unfollow(self):
        self.client.force_authenticate(self.user)
        url = reverse('api_user_follow', args=[self.other.id])
        self.assertTrue(self.client.post(url).data['is_following'])
        followers = self.client.get(reverse('api_user_followers', args=[self.other.id]))
        self.assertEqual(followers.data['count'], 1)
        self.assertFalse(self.client.delete(url).data['is_following'])

    def test_cannot_follow_self(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('api_user_follow', args=[self.user.id]))
        self.assertEqual(response.status_code, 400)

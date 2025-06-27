from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CredentialsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='tester1@gmail.com', password='test123!')
        test_user2 = User.objects.create_user(username='tester2@ncsu.edu', password='test456!')

    def test_credential_create_view_redirect_to_login(self):
        response = self.client.get(reverse('credential_create'))
        self.assertRedirects(response, '/accounts/login/?next=/credentials/create')
        self.assertEqual(response.status_code, 302)
    
    def test_credential_create_view_login(self):
        self.client.login(username='tester1@gmail.com', password='test123!')
        response = self.client.get(reverse('credential_create'))
        self.assertEqual(str(response.context['user']), 'tester1@gmail.com')
        self.assertEqual(response.status_code, 200)

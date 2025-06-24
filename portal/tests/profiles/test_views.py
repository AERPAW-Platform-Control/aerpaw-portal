import unittest
from django.contrib.auth import authenticate, login
from django.db.models import Q
from urllib.parse import urlencode
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser

User = get_user_model()

class TestProfileView(TestCase):
    fixtures = [
        'portal/tests/test_fixtures/test_aerpaw_roles.json',
        'portal/tests/test_fixtures/test_experiment_files.json',
        'portal/tests/test_fixtures/test_experiments.json',
        'portal/tests/test_fixtures/test_operations.json',
        'portal/tests/test_fixtures/test_profiles.json',
        'portal/tests/test_fixtures/test_projects.json',
        'portal/tests/test_fixtures/test_resources.json',
        'portal/tests/test_fixtures/test_users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='tester1@gmail.com', password='test123!')
        test_user1.groups.set([1])
        test_user1.save()
        test_user2 = User.objects.create_user(username='tester2@ncsu.edu', password='test456!')
        test_user2.groups.set([1,2,3,4])
        test_user2.save()

    def setUp(self):        
        self.user = AerpawUser.objects.get(email='tester1@ncsu.edu')
        self.client.force_login(self.user)
    
    def test_user_is_operator(self):
        response = self.client.get(reverse('profile'))
        is_operator = response.context['user'].is_operator()
        self.assertTrue(is_operator)

    def test_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.context['user'].username, 'tester1@ncsu.edu')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('profile.html')

    def test_profile_context(self):
        """  
        Tests for the correct context:
        - user
        - user_data
        - user_profile
        - user_tokens
        - user_credentials
        - user_messages
        - user_requests
        - unread_message_count
        - message
        - debug
        """
        
        response = self.client.get(reverse('profile'))
        user = response.context["user"]
        user_data = response.context["user_data"]
        user_profile = response.context["user_profile"]
        print(f'rc user tokens: {response.context["user_tokens"]}')
        print(f'rc creds: {response.context["user_credentials"]}')
        self.assertEqual(user, self.user)

        self.assertEqual(user_data['aerpaw_roles'], [role.name for role in self.user.groups.all()])
        self.assertEqual(user_data['display_name'], self.user.display_name)
        self.assertEqual(user_data['email'], self.user.email)
        self.assertEqual(user_data['is_active'], self.user.is_active)
        self.assertEqual(user_data['openid_sub'], self.user.openid_sub)
        self.assertEqual(user_data['user_id'], self.user.id)
        self.assertEqual(user_data['username'], self.user.username)

        self.assertEqual(user_profile['employer'], self.user.profile.employer)
        self.assertEqual(user_profile['position'], self.user.profile.position)
        self.assertEqual(user_profile['research_field'], self.user.profile.research_field)

        
    
    def test_not_user(self):
        """  
        Tests that the handle_error decorator will catch the first exception
        if the user is not found
        """
        pass

    def test_2nd_exception(self):
        """  
        Tests that the view will still show the template correctly if there is an exception
        while gathering the variables for the context
        """
        pass

    def test_post_display_name(self):
        """  
        Tests that the display name is updated and displayed correctly after the user makes edits
        """
        pass

    def test_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed('error_handling/error_template.html')

    

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
@unittest.skip("Skipping all tests in this class")
class TestExperimentListView(TestCase):
    fixtures = ['aerpaw_roles', 'experiments', 'experiment_files', 'operations', 'profiles', 'projects',  'resources', 'users',]
    #fixtures = ['aerpaw_roles']

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='tester1@gmail.com', password='test123!')
        test_user1.groups.set([1])
        test_user1.save()
        test_user2 = User.objects.create_user(username='tester2@ncsu.edu', password='test456!')
        test_user2.groups.set([1,2,3,4])
        test_user2.save()
    
    def test_user_is_operator(self):
        self.client.login(username='tester2@ncsu.edu', password='test456!')
        response = self.client.get(reverse('experiment_list'))
        is_operator = response.context['user'].is_operator()
        self.assertTrue(is_operator)

    def test_login(self):
        self.client.login(username='tester2@ncsu.edu', password='test456!')
        response = self.client.get(reverse('experiment_list'))
        self.assertEqual(response.context['user'].username, 'tester2@ncsu.edu')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('experiment_list.html')

    def test_experiments_present_for_ops(self):
        self.client.login(username='tester2@ncsu.edu', password='test456!')
        og_count = AerpawExperiment.objects.filter(is_deleted=False).count()
        response = self.client.get(reverse('experiment_list'))
        self.assertEqual(response.context['count'], og_count)
    
    def test_experiments_present_for_experimenter(self):
        self.client.login(username='tester1@gmail.com', password='test123!')
        user = User.objects.get(username='tester1@gmail.com')
        og_count = AerpawExperiment.objects.filter(
                    Q(is_deleted=False) &
                    (Q(project__project_membership__email__in=[user.email]) | Q(project__project_creator=user))
                ).count()
        response = self.client.get(reverse('experiment_list'))
        self.assertEqual(response.context['count'], og_count)

    def test_logged_out_user(self):
        response = self.client.get(reverse('experiment_list'))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/experiments/')

class TestExperimentDetailView(TestCase):
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
        user1 = AerpawUser.objects.get(id=2)
        user1.set_password('test456!')
        user1.save()
        user2 = AerpawUser.objects.get(id=3)
        user2.set_password('test123!')
        user2.save()


    def test_login_ops_user(self):
        self.client.login(username='tester1@ncsu.edu', password='test456!')
        response = self.client.get(reverse('experiment_detail', args=[1]))
        self.assertEqual(response.context['user'].username, 'tester1@ncsu.edu')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('experiment_detail.html')
    
    def test_login_experimenter_with_own_experiment(self):
        self.client.login(username='tester2@gmail.com', password='test123!')
        response = self.client.get(reverse('experiment_detail', args=[2]))
        self.assertEqual(response.context['user'].username, 'tester2@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('experiment_detail.html')
    
    def test_login_experimenter_as_experiment_non_member(self):
        self.client.login(username='tester2@gmail.com', password='test123!')
        response = self.client.get(reverse('experiment_detail', args=[1]))
        self.assertEqual(response.context['user'].username, 'tester2@gmail.com')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('experiment_detail.html')

    def test_logged_out_user(self):
        response = self.client.get('/experiments/1')
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/experiments/1')

    def test_experiment_does_not_exist(self):
        self.client.login(username='tester1@ncsu.edu', password='test456!')
        response = self.client.get(reverse('experiment_detail', args=[123]))
        self.assertRedirects(response, '/accounts/login/?next=/experiments/1')

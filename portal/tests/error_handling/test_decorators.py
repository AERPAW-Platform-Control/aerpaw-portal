from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ErrorHandlingDecoratorTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='tester1@gmail.com', password='test123!')
        test_user2 = User.objects.create_user(username='tester2@ncsu.edu', password='test456!')

    """ def setUp(self):
        return super().setUp() """
    
    def test_experiment_detail_view_error(self):
        self.client.get(reverse('experiment_detail'))

    
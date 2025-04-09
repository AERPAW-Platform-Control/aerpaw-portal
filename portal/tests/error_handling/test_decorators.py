import os
from django.test import TestCase


class TestErrorHandlingDecorator(TestCase):
    
    @classmethod
    def setUp(self):
        return super().setUp()
    
    def test_experiment_detail_view_error(self):
        self.client.get('/experiments/detial')
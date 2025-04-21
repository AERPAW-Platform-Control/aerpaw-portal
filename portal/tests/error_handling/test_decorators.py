from django.test import Client, TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render

from portal.apps.error_handling.decorators import handle_error
from portal.apps.error_handling.api.error_utils import catch_exception
from portal.apps.experiments.views import experiment_list
from portal.apps.users.models import AerpawUser

User = get_user_model()

class ErrorHandlingDecoratorTest(TestCase):
    #fixtures = ['aerpaw_roles', 'experiments', 'experiment_files', 'operations', 'profiles', 'projects',  'resources', 'users',]
    fixtures = ['aerpaw_roles', 'profiles', 'users']
    
    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='tester1@gmail.com', password='test123!')
        test_user1.groups.set([1])
        test_user1.save()
        test_user2 = User.objects.create_user(username='tester2@ncsu.edu', password='test456!')
        test_user2.groups.set([1,2,3,4])
        test_user2.save()

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.client.login(username='tester2@ncsu.edu', password='test456!')
        self.user = AerpawUser.objects.get(username='tester2@ncsu.edu')

    def test_view_with_error(self):

        @handle_error
        def experiment_list(request):
            try:
                raise AttributeError()
            except AttributeError as exc:
                catch_exception(exc, request)
            return HttpResponse("OK")

        
        request = self.factory.get("/experiment_list")
        request.user = self.user

        session_middleware = SessionMiddleware(lambda r:r)
        session_middleware.process_request(request)
        request.session.save()
        
        message_middleware = MessageMiddleware(lambda r:r)
        message_middleware.process_request(request)
        request.session = self.client.session

        response = experiment_list(request)

        message_middleware.process_response(request, response)
    
        print(f'messages: {list(get_messages(request))}')
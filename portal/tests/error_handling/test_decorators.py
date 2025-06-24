from django.test import Client, TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.exceptions import PermissionDenied

from portal.apps.error_handling.decorators import handle_error
from portal.apps.error_handling.models import AerpawError, AerpawErrorGroup
from portal.apps.error_handling.api.error_utils import catch_exception
from portal.apps.experiments.views import experiment_list
from portal.apps.users.models import AerpawUser

User = get_user_model()

class ErrorHandlingDecoratorTest(TestCase):
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
        self.client = Client()
        self.factory = RequestFactory()

    def test_view_with_error(self):
        """  
        This test does a general check to see if the decorator creates a django message
        """
        # test function with decorator attached and error present
        @handle_error
        def test_func1(request):
            try:
                raise AttributeError()
            except AttributeError as exc:
                catch_exception(exc, request)
            return HttpResponse("OK")
        
        # login the test user and get the AerpawUser obj
        self.client.login(username='tester2@ncsu.edu', password='test456!')
        self.user = AerpawUser.objects.get(username='tester2@ncsu.edu')

        # create the request
        request = self.factory.get("/test_func1")
        request.user = self.user

        # install django session middleware
        session_middleware = SessionMiddleware(lambda r:r)
        session_middleware.process_request(request)
        request.session.save()
        
        # install django message middleware
        message_middleware = MessageMiddleware(lambda r:r)
        message_middleware.process_request(request)
        request.session = self.client.session

        # call the test view function
        response = test_func1(request)

        # get the messages
        message_middleware.process_response(request, response)
        messages = list(get_messages(request))

        # make assertions
        self.assertEqual(len(messages), 1)          # One message should be present
        self.assertEqual(messages[0].level, 20)     # The Message level should be Info or 20

    def test_error_obj_create(self):
        """  
        This tests for the creation of an AerpawError Object
            - The id for the error created in this test is 2 becuase the 
            first error object should be created in the test before this one.
        """
        # test function with decorator attached and error present
        @handle_error
        def test_view(request):
            try:
                raise AttributeError()
            except AttributeError as exc:
                catch_exception(exc, request)
            return HttpResponse("OK")

        # login the test user and get the AerpawUser obj
        self.client.login(username='tester2@ncsu.edu', password='test456!')
        self.user = AerpawUser.objects.get(username='tester2@ncsu.edu')

        # create the request
        request = self.factory.get("/test_view")
        request.user = self.user

        # install django session middleware
        session_middleware = SessionMiddleware(lambda r:r)
        session_middleware.process_request(request)
        request.session.save()
       
        # install django message middleware
        message_middleware = MessageMiddleware(lambda r:r)
        message_middleware.process_request(request)
        request.session = self.client.session

        
        # Delete the current errors in the database before calling the test view
        AerpawError.objects.all().delete()

        # call the test view function
        test_view(request)

        # get the error objects
        error = list(AerpawError.objects.all())

        # make assertions
        self.assertEqual(error[0].id, 3)                    # The error id should be equal to 3
        self.assertEqual(error[0].type, 'AttributeError')   # the error type is AttributeError

    def test_error_group_create(self):
        """  
        This tests for the creation of an AerpawErrorGroup Object
            - The id for the errors created in this test are 3 and 4 becuase the 
            first two error objects should have been created in the tests before this one.
        """
        # test function with decorator attached and 2 errors present
        @handle_error
        def test_func3(request):
            try:
                raise AttributeError()
            except AttributeError as exc:
                catch_exception(exc, request)

            try:
                raise TypeError()
            except TypeError as exc:
                catch_exception(exc, request)

            return HttpResponse("OK")

        # login the test user and get the AerpawUser obj
        self.client.login(username='tester2@ncsu.edu', password='test456!')
        self.user = AerpawUser.objects.get(username='tester2@ncsu.edu')

        # create the request
        request = self.factory.get("/test_func3")
        request.user = self.user

        # install django session middleware
        session_middleware = SessionMiddleware(lambda r:r)
        session_middleware.process_request(request)
        request.session.save()
        
        # install django message middleware
        message_middleware = MessageMiddleware(lambda r:r)
        message_middleware.process_request(request)
        request.session = self.client.session

        # delete all the errors before test_func is called
        AerpawError.objects.all().delete()
        
        # call the test view function
        test_func3(request)

        # get the error objects and error group object
        errors = AerpawError.objects.all().order_by('datetime')
        err_group = AerpawErrorGroup.objects.latest('datetime')

        # make assertions
        self.assertEqual(list(err_group.errors.all()), list(errors))    # all the caught errors are also in the group
        self.assertEqual(err_group.view_name, 'unknown')                # the group name is unknown because only a test view is called
        self.assertEqual(err_group.id, 1)                               # the group id should be equal to one

    def test_view_with_permission_error(self):
        """  
        This tests to see if the decorator redirects to the correct html template when a permission exception is caught
        """
        # Log out the current user
        self.client.logout()

        # log in a user without the correct credentials/roles
        self.client.login(username='tester1@gmail.com', password='test123!')
        self.user = AerpawUser.objects.get(username='tester1@gmail.com')

        # call the experiment detail view for an experiment that the user is not a member or owner
        response = self.client.get(reverse('experiment_detail', args=[1]))

        # Get the messages created during the view request
        messages = list(get_messages(response.wsgi_request))

        # Make assertions
        self.assertTemplateUsed(response, 'error_handling/error_template.html') # The decorator should redirect to the error_template due to PermissionDenied error
        self.assertEqual(len(messages), 1)                                      # Only one message should be present
        self.assertEqual(messages[0].level, 50)                                 # The message level should be a custom level of 50 or Permission Type Error
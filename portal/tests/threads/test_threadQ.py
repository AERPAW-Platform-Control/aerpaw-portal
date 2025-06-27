import unittest, importlib, datetime, time
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from urllib.parse import urlencode
from django.test import TestCase
from django.test import RequestFactory
from django.urls import reverse
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from portal.apps.credentials.models import PublicCredentials
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.projects.models import AerpawProject
from portal.apps.operations.models import CanonicalNumber
from portal.apps.resources.models import AerpawResource
from portal.apps.threads.models import ThreadQue
from portal.apps.users.models import AerpawUser
from rest_framework.test import APIRequestFactory
from django.test import TransactionTestCase

from django.db import connection

def kill_other_database_sessions(database_name='test_postgres'):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s
              AND pid <> pg_backend_pid();
        """, [database_name])

User = get_user_model()

class TestThreadQ(TransactionTestCase):
    fixtures = [
        'portal/tests/test_fixtures/test_aerpaw_roles.json',
        'portal/tests/test_fixtures/test_experiment_files.json',
        #'portal/tests/test_fixtures/test_experiments.json',
        'portal/tests/test_fixtures/test_operations.json',
        'portal/tests/test_fixtures/test_profiles.json',
        'portal/tests/test_fixtures/test_projects.json',
        'portal/tests/test_fixtures/test_resources.json',
        'portal/tests/test_fixtures/test_threads.json',
        'portal/tests/test_fixtures/test_users.json'
        ]
    
    """ @classmethod
    def setUpTestData(cls): """

        
        
    def setUp(self):
        kill_other_database_sessions(database_name='test_postgres')
        self.factory = APIRequestFactory()
        test_user1 = User.objects.create_user(id=1, email='tester1@gmail.com', username='tester1@gmail.com', password='test123!', created=timezone.make_aware(datetime.datetime.now()))
        test_user1.groups.set([1])
        test_user1.save()

        for i in range(1, 3):
            canNum = CanonicalNumber.objects.create(canonical_number=i)
            canNum.save()

            exp = AerpawExperiment(
                created_by=test_user1.email,
                modified_by=test_user1.email,
                canonical_number=canNum,
                description='Testing Only',
                experiment_creator=test_user1,
                experiment_flags='000',
                experiment_state='saved',
                is_canonical=True,
                is_deleted=False,
                is_emulation_required=True, 
                is_retired=False,
                name=f'TestExp{i}',
                project=AerpawProject.objects.get(id=1),
            )
            exp.save()
            resources = AerpawResource.objects.filter(id__in = [4,5])
            exp.resources.add(resources[0])
            exp.resources.add(resources[1])
            
        
        print(f'Number of Experiments for testing: {AerpawExperiment.objects.all().count()}')
        
        

    def test_fixtures_loaded(self):
        wdd = ThreadQue.objects.get(target='wait_development_deploy')
        self.assertEqual(wdd.target, 'wait_development_deploy')
        self.assertEqual(30, AerpawExperiment.objects.count())

        
    
    def test_exps_in_threadQue(self):
        self.factory = APIRequestFactory()
        threadQ = ThreadQue.objects.get(target='wait_development_deploy')
        print(f'Target: {threadQ.target}')
        module = importlib.import_module('portal.apps.experiments.api.experiment_utils')
        saved_to_wait_development_deploy = getattr(module, 'saved_to_wait_development_deploy')
        exps = AerpawExperiment.objects.all()
        
        for exp in exps:
            try: 
                user = exp.experiment_creator
                print(f'USER is Experimenter: {user.groups.all()}')
                request = self.factory.get('/')
                request.user = user
                print(f'USER= {user}')
                que_number=saved_to_wait_development_deploy(request, exp)
                print(f'QUE NUMBER: {que_number}')
            except Exception as exc:
                print(exc)

        que = threadQ.threads.all().order_by('thread_created')
        que_length = que.count()
        while que_length != 0:
            time.sleep(5)
            print()
            print('Testing...')
            que = threadQ.threads.all().order_by('thread_created')
            que_length = que.count()
            print(f'Que Length: {que_length}')
            print(f'Waiting for que to finish...')
            print()

        print(f'Experiments: {len(exps)+1}\n QueLength: {que_length}')
        print(f'threadQ is threading: {threadQ.is_threading}')
        self.assertEqual(que_length, 0)
        self.assertFalse(threadQ.is_threading)
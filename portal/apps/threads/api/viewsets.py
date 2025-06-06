import time, threading
from uuid import uuid4
from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import MethodNotAllowed, NotFound, PermissionDenied, ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions

from portal.apps.experiments.models import AerpawExperiment
from portal.apps.user_messages.user_messages import p
from portal.apps.threads.api.serializers import AerpawThreadSerializer, ThreadQueSerializer
from portal.apps.threads.models import AerpawThread, ThreadQue
from portal.server.settings import MOCK_OPS



class AerpawThreadViewset(GenericViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = AerpawThread.objects.all().order_by('user')
    serializer_class = AerpawThreadSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_operator():
            queryset = AerpawThread.objects.order_by('thread_start')
        else:
            queryset = AerpawThread.objects.filter(Q(user=user)).order_by('thread_start')
        return queryset

    def create(self, *args, **kwargs):
        action = kwargs.get('action').upper()
        new_thread = AerpawThread(
            user=kwargs.get('user'),
            uuid=uuid4(),
            experiment=AerpawExperiment.objects.get(id=kwargs.get('exp_id')),
            displayed=False,
            action=action,
            command=kwargs.get('command'),
        )
        new_thread.save()
        self.add_to_que(new_thread)
        print(f'New AerpawThread: thread# {new_thread.id}')
        return new_thread

    def update(self, thread, exit_code, response, **kwargs) -> None:
        thread = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        thread.thread_end = timezone.now()
        thread.exit_code = kwargs.get('exit_code')
        thread.response = kwargs.get('response')
        thread.save()
        message_components = {
            'message_body': thread.message, 
            'message_owner':thread.user.id, 
            'message_subject':f'{thread.get_action_display()} for Experiment: {thread.experiment.id}',
            'recieved_by':thread.user.id
            }
        # portal_error_message(thread.user, None, **message_components)
        print(f'AerpawThread ended: thread# {thread.id}')

    def retrieve(self, request, *args, **kwargs):
        thread = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        user = request.user
        if thread.user == user or user.is_operator() == True:
            serializer = AerpawThreadSerializer(thread)
            du = dict(serializer.data)
            response_data = {
                'thread_id':du.get('thread_id'),
                'user_id': du.get('user_id'),
                'experiment_id': du.get('experiment_id'),
                'thread_start': du.get('thread_start'),
                'thread_end': du.get('thread_end'),
                'exit_code': du.get('exit_code'),
                'response': du.get('response'),
                'is_error': du.get('is_error'),
                'error_id': du.get('error_id'),
                'thread_uuid': du.get('thread_uuid'),
            }
            return response_data
        else:
           
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /aerpaw_thread/{0} details".format(kwargs.get('pk')))
        
    def add_to_que(self, request, *args, **kwargs):
        thread = get_object_or_404(self.queryset, pk=kwargs.get('id'))

        request.query_params = QueryDict('', mutable=True)
        request.query_params.update({'name':thread.action, 'thread_id': thread.id})
        threadQ = ThreadQueViewset(request)
        threadQ.update(request, kwargs={'add': thread.id, 'name':thread.action})
        threadQ.run_que(request)
        
        if thread not in threadQ.threads.all():
            threadQ.threads.add(self)
            threadQ.save()
            ThreadQueViewset.run_que(request)
            

class ThreadQueViewset(GenericViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = ThreadQue.objects.all()
    serializer_class = ThreadQueSerializer

    def get_queryset(self):
        que_name = self.request.query_params.get('name', None)
        queryset = None
        if que_name:
            try:
                queryset = ThreadQue.objects.filter(name=que_name)
            except Exception as exc:
                print(f'ThreadQue named {que_name} NOT FOUND')

        return queryset
    
    def update(self, request, kwargs):
        """  
        For the addition and removal of threads from the thread que
        """
        threadQ = self.get_queryset()[0]
        add = kwargs.get('action')
        if kwargs.get('add'):
            thread = get_object_or_404(AerpawThreadViewset.queryset, pk=kwargs.get('thread_id'))
            threadQ.threads.add(thread)
        else:
            threadQ.threads.remove(thread)
        threadQ.save()
        

    def retrieve(self, *args, **kwargs):
        thread = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        user = self.request.user
        if thread.user == user or user.is_operator() == True:
            serializer = ThreadQueSerializer(thread)
            du = dict(serializer.data)
            print(f'ThreadQue data: {du}')
            response_data = {
                'id':du.get('id'),
                'is_threading': du.get('is_threading'),
                'name': du.get('name'),
                'target': du.get('target'),
                'threads': du.get('threads')
            }
            return response_data
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /aerpaw_thread/{0} details".format(kwargs.get('pk')))

    def run_que(self, request):
        mock = MOCK_OPS
        threadQ = self.retrieve()
        if threadQ.is_threading == False:
            #threadQ.is_threading = True
            #threadQ.save()
            self.update()
            while len(threadQ.threads) > 0:
                threads = threadQ.threads
                threads.sort(key=lambda thread: thread.thread_created)
                print(f'The {threadQ.name} Que is running the threads ...')
                [print(f'{thread.id} | {thread.thread_created}') for thread in threads]
                thread1 = threads[0]
                print(f'Thread {thread1.id} for Experiment {thread1.experiment.id} is starting.')
                if thread1.is_threaded == False:
                    # start the thread
                    ssh_thread = threading.Thread(target=threadQ.target, args=(request, thread1.experiment, thread1.command, mock, thread1))
                    ssh_thread.start()
                    thread_vs = AerpawThreadViewset()
                    thread_vs.update(thread1.id, kwargs={'threaded': True})
                    #thread1.threaded = True
                    #thread1.save()

                if thread1.is_threaded == True:
                    # wait 20 seconds for the command script to run and recheck the thread for an ending or get the next thread in line
                    time.sleep(20)
                    

            #threadQ.is_threading = False
            #threadQ.save()
            self.update()
            threadQ = self.retrieve()
        else:
            print(f'The {threadQ.name} Que is already running')
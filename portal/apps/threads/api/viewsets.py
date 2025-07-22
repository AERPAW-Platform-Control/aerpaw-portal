import time, threading, importlib
from uuid import uuid4
from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import MethodNotAllowed, NotFound, PermissionDenied, ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions

from portal.apps.experiments.models import AerpawExperiment
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
            queryset = AerpawThread.objects.order_by('thread_created')
        else:
            queryset = AerpawThread.objects.filter(Q(user=user)).order_by('thread_created')
        return queryset

    def create(self, request, *args, **kwargs):
        target = kwargs.get('target').lower()
        new_thread = AerpawThread(
            user=request.user,
            uuid=uuid4(),
            experiment=AerpawExperiment.objects.get(id=kwargs.get('exp_id')),
            displayed=False,
            target=target,
            command=kwargs.get('command'),
        )
        new_thread.save()
        print(f'New AerpawThread: thread# {new_thread.id}')
        return new_thread

    def update(self, **kwargs) -> None:
        thread = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        print(f'THREAD: {thread.id} {thread}')
        print('EXIT_CODE:', kwargs.get('exit_code'))
        thread.is_threaded = kwargs.get('threaded') if kwargs.get('threaded') else thread.is_threaded
        thread.thread_end = timezone.now() if kwargs.get('exit_code') else None
        thread.exit_code = kwargs.get('exit_code') if kwargs.get('exit_code') else None
        thread.response = kwargs.get('response') if kwargs.get('response') else None
        thread.save()
        print(f'thread.exit_code: {thread.exit_code}')
        message_components = {
            'message_body': thread.message, 
            'message_owner':thread.user.id, 
            'message_subject':f'{thread.get_target_display()} for Experiment: {thread.experiment.id}',
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
        print(f'target= {thread.target}')
        threadQ = ThreadQueViewset()
        print(f'Adding thread to que')
        threadQ.update(target=thread.target, thread_id=thread.id)
        print('running thread que')
        que_thread = threading.Thread(target=threadQ.run_que, args=[request], kwargs={'target':thread.target})
        que_thread.start()
        """ que_number_thread = threading.Thread(target=func, args=(request, thread1.experiment, thread1.command, MOCK_OPS, thread1)) """
        threads=threadQ.get_queryset(target=thread.target).threads.all().order_by('thread_created')
        que_number = list(threads).index(thread)
        print(f'Que Number: {que_number}')
        return que_number
    
    def remove_from_que(self, request, *args, **kwargs):
        thread = get_object_or_404(self.queryset, pk=kwargs.get('id'))
        print(f'target= {thread.target}')
        threadQ = ThreadQueViewset()
        print(f'Removing thread from que')
        threadQ.update(target=thread.target, thread_id=thread.id)
        
    def get_que_number(self, *args, **kwargs):
        
        thread = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        while not thread.thread_end: 
            threadQ = ThreadQueViewset()
            threads=threadQ.get_queryset(target=thread.target).threads.all().order_by('thread_created')
            que_number = list(threads).index(thread)
            thread = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
            time.sleep(20)
        print(f'QUE NUMBER: {que_number}')
        return que_number

class ThreadQueViewset(GenericViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = ThreadQue.objects.all()
    serializer_class = ThreadQueSerializer

    def get_queryset(self , **kwargs):
        que_target = kwargs.get('target', None)
        print(f'que_target: {que_target}')
        queryset = None
        if que_target:
            try:
                queryset = ThreadQue.objects.get(target=que_target.lower())
                print(f'threadQ(s): {queryset}')
            except Exception as exc:
                print(f' NOT FOUND! ThreadQue with target: {que_target}')
            print(f'threadQ(s): {queryset}')
        if kwargs.get('pk'):
            queryset = ThreadQue.objects.get(id=kwargs.get('pk'))
        return queryset
    
    def update(self, **kwargs):
        """  
        For the addition and removal of threads from the thread que
        """
        print(f'target in update: {kwargs.get("target")}')
        threadQ = self.get_queryset(target=kwargs.get('target'))
        thread = get_object_or_404(AerpawThreadViewset.queryset, pk=kwargs.get('thread_id'))
        
        if thread not in threadQ.threads.all():
            threadQ.threads.add(thread)
        else:
            threadQ.threads.remove(thread)

        if threadQ.threads.count() == 0:
            threadQ.is_threading = False

        threadQ.save()
        
    def retrieve(self, *args, **kwargs):
        threadQ = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        user = self.request.user
        if threadQ.user == user or user.is_operator() == True:
            serializer = ThreadQueSerializer(threadQ)
            du = dict(serializer.data)
            print(f'ThreadQue data: {du}')
            response_data = {
                'id':du.get('id'),
                'is_threading': du.get('is_threading'),
                'target': du.get('target'),
                'threads': du.get('threads')
            }
            return response_data
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /aerpaw_thread/{0} details".format(kwargs.get('pk')))

    def run_que(self, request, **kwargs):
        threadQ = self.get_queryset(target=kwargs.get('target'))
        print(f'ThreadQ retrieved is: {threadQ.target}')
        print(f'ThreadQ is running: {threadQ.is_threading}')
        if threadQ.is_threading == False:
            threadQ.is_threading = True
            threadQ.save()
            print(f'The {threadQ.target} Que is running ...')
            while threadQ.is_threading:
                threads = threadQ.threads.all().order_by('thread_created')
                print(f'\nNumber of threads remaining: {threads.count()}')
                [print(f'{thread.id} | {thread.thread_created}') for thread in threads]
                thread1 = threads[0]
                if thread1.is_threaded == False:
                    print(f'Thread {thread1.id} for Experiment {thread1.experiment.id} is starting.')
                    thread_vs = AerpawThreadViewset()
                    thread_vs.update(pk=thread1.id, threaded=True)

                    module_path, func_name = 'portal.apps.experiments.api.experiment_utils.wait_development_deploy'.rsplit('.', 1)
                    module = importlib.import_module('portal.apps.experiments.api.experiment_utils')
                    func = getattr(module, thread1.target)
                    print(f'function: {func}')

                    target_thread = threading.Thread(target=func, args=(request, thread1.experiment, thread1.command, MOCK_OPS, thread1))
                    target_thread.start()

                    if MOCK_OPS:
                        time.sleep(5)
                    else: 
                        time.sleep(20)

                elif thread1.is_threaded == True and thread1.thread_end == None:
                    # wait 20 seconds for the command script to run and recheck the thread for an ending or get the next thread in line
                    print(f'waiting another 20 seconds for thread {thread1.id} to complete')
                    if MOCK_OPS:
                        time.sleep(5)
                    else: 
                        time.sleep(20)

                elif thread1.is_threaded == True and thread1.thread_end != None:
                    print(f'thread {thread1.id} completed with exit code {thread1.exit_code}. Updating threadQue')
                    self.update( target=threadQ.target, thread_id=thread1.id)

                threadQ = self.get_queryset(target=thread1.target)
                if threadQ.is_threading == False:
                    print(f'ThreadQ {threadQ.target} finished all threads!')
                    
                    
        else:
            print(f'The {threadQ.target} Que is already running')

    



    def call_function_by_path(path):
        module_path, func_name = path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        return func()




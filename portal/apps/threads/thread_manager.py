import traceback, logging, datetime, os, uuid, time
import threading
from django.apps import apps
from django.utils import timezone
from uuid import uuid4

from portal.apps.error_handling.models import AerpawError
from portal.apps.error_handling.error_dashboard import portal_error_message
from portal.apps.threads.models import AerpawThread, ThreadQue
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser



def end_aerpaw_thread(thread: AerpawThread, exit_code, response) -> None:
    
    thread.thread_end = timezone.now()
    thread.exit_code = exit_code
    thread.response = response
    thread.save()
    message_components = {
        'message_body': thread.message, 
        'message_owner':thread.user.id, 
        'message_subject':f'{thread.get_action_display()} for Experiment: {thread.experiment.id}',
        'recieved_by':thread.user.id
        }
    portal_error_message(thread.user, None, **message_components)
    print(f'AerpawThread ended: thread# {thread.id}')
            
def add_to_que(self, request):
        threadQ = ThreadQue.objects.get(name=str(self.action))
        if self not in threadQ.threads.all():
            threadQ.threads.add(self)
            threadQ.save()
            threadQ.run_que(request)
           
def run_thread_que(request, threadQ):
    mock = MOCK_OPS
    if threadQ.is_running() == False:
        threadQ.is_threading = True
        threadQ.save()
        while len(threadQ.threads.all()) > 0:
            threads = threadQ.threads.all()
            threads.sort(key=lambda thread: thread.thread_created)
            print(f'The {threadQ.name} Que is running the threads ...')
            [print(f'{thread.id} | {thread.thread_created}') for thread in threads]
            thread1 = threads[0]
            print(f'Thread {thread1.id} for Experiment {thread1.experiment.id} is starting.')
            if thread1.is_threaded == False:
            # start the thread
                
                ssh_thread = threading.Thread(target=threadQ.target, args=(request, thread1.experiment, thread1.command, mock, thread1))
                ssh_thread.start()
                thread1.threaded = True
                thread1.save()
            if thread1.is_threaded == True:
                # wait 20 seconds for the command script to run and recheck the thread for an ending or get the next thread in line
                time.sleep(20)
                

        threadQ.is_threading = False
        threadQ.save()
    else:
        print(f'The {threadQ.name} Que is already running')

    def is_running(self):
        return self.is_threading


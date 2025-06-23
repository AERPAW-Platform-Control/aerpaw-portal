import json
from datetime import datetime
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from portal.apps.threads.models import AerpawThread

# Create your views here.

class AerpawSSHErrorHandling(View):

    def post(self, request):
        threads = None
        user = request.user
        response_data = {'threads':[]}
        if json.loads(request.body)['action'] == 'threads_exist':
            threads = AerpawThread.objects.filter(user=user, displayed=False)
            if not threads:
                return JsonResponse({'threads':'NoneFound'})
            else:
                for thread in threads:
                    response_data['threads'].append( {str(thread): {
                        'id':str(thread.id), 
                        'is_error':str(thread.is_error),
                        'message': str(thread.message),
                        'completed': True if thread.thread_end else False,
                        'is_success':True if thread.exit_code == 0 else False,
                        }})
                return JsonResponse(response_data)

        if json.loads(request.body)['action'] == 'incomplete_threads':   
            threads = AerpawThread.objects.filter(user=user, displayed=False)
            for thread in threads:
                response_data['threads'].append( {str(thread): {
                    'id':str(thread.id), 
                    'is_error':str(thread.is_error),
                    'message': str(thread.message),
                    'completed': True if thread.thread_end else False,
                    'is_success':True if thread.exit_code == 0 else False,
                    }})
            return JsonResponse(response_data)

        if json.loads(request.body)['action'] == 'mark_displayed':
            threads = [AerpawThread.objects.get(id=int(thread_id)) for thread_id in json.loads(request.body)['displayed_threads']]
            for thread in threads:
                thread.displayed = True
                thread.save()
            return JsonResponse({'success':True})
import json
from datetime import datetime
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from .error_dashboard import new_error, reduce_stored_errors
from portal.apps.error_handling.models import AerpawError
from portal.apps.experiment_info.form_dashboard import upload_old_form_data
from portal.apps.users.models import AerpawUser

# Create your views here.
class ErrorHandlingView(View):

    def get(self, request):
        message = None
        is_operator = request.user.is_operator()
        if is_operator == True:
            context={
                'message':message,
                'is_operator':is_operator,
            }
            return render(request, 'error_handling/error_dashboard.html', context)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to view errors")
            except PermissionDenied as exc:
                new_error(exc, request.user)
    
    def post(self, request):
        request_body = json.loads(request.body)
        action = request_body['action']
        
        if action == 'get_undisplayed_errors':
            errors = AerpawError.objects.filter(displayed = False, user=request.user)
            if not errors:
                return JsonResponse({'errors':'None'})
            else:
                response = {'errors':[]}
                for error in errors:
                    response['errors'].append({
                        'id':str(error.id),
                        'message':error.message
                    }) 
                return JsonResponse(response)
            
        if action == 'mark_errors_displayed':
            error_ids = request_body['error_ids']
            errors = AerpawError.objects.filter(displayed = False, user=request.user)
            for error in errors:
                if str(error.id) in error_ids:
                    error.displayed = True
                    error.save()
            return JsonResponse({'success':True})
        
        


class ErrorDashboardView(View):
    def get(self, request):
        message = None
        #upload_old_form_data()
        is_operator = request.user.is_operator()
        if is_operator == True:
            context={
                'users':AerpawUser.objects.all(),
                'message':message,
                'is_operator':is_operator,
            }
            return render(request, 'error_handling/error_dashboard.html', context)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to view errors")
            except PermissionDenied as exc:
                new_error(exc, request.user)

            context = {
                    'users':[],
                    'errors':[],
                    'message':'',
                }
            return render(request, 'error_handling/error_dashboard.html', context)

    def post(self, request):
        users = []
        errors = []
        notice = ''
        is_operator = request.user.is_operator()
        if is_operator == True:
            users = AerpawUser.objects.all().order_by('email')
            if 'get_error_by_id' in request.POST:
                try:
                    errors = [AerpawError.objects.get(id=int(request.POST.get('error-by-id')))]
                except:
                    notice = f'No errors with an id of {request.POST.get("error-by-id")} found.'
            if 'get_error_by_filter' in request.POST:
                # convert the date input into proper format for querying
                if request.POST.get("error-by-daterange-start") != '':
                    daterange_start = timezone.make_aware(
                        datetime(
                            int(request.POST.get("error-by-daterange-start").split('-')[0]),
                            int(request.POST.get("error-by-daterange-start").split('-')[1]),
                            int(request.POST.get("error-by-daterange-start").split('-')[2]),
                            )
                        )
                else:
                    daterange_start = None

                # convert the date input into proper format for querying
                if request.POST.get("error-by-daterange-end") != '':
                    daterange_end = timezone.make_aware(
                        datetime(
                            int(request.POST.get("error-by-daterange-end").split('-')[0]),
                            int(request.POST.get("error-by-daterange-end").split('-')[1]),
                            int(request.POST.get("error-by-daterange-end").split('-')[2]),
                            )
                        )
                else:
                    daterange_end = None

                # create a dictionary of all the filters    
                filter_kwargs = {
                    'type': request.POST.get("error-by-type") if request.POST.get("error-by-type") != 'null' else None,
                    'user': request.POST.get("error-by-user") if request.POST.get("error-by-user") != 'null' else None,
                    'datetime__range':(daterange_start, daterange_end) if daterange_start is not None and daterange_end is not None else None,
                    
                    }
                
                # Sort the dictionary to remove all the filters that are None
                filter_kwargs = {field: value for field,value in filter_kwargs.items() if value != None}

                # Query AerpawError with dictionary
                errors = AerpawError.objects.filter(**filter_kwargs).order_by('datetime')

                # Create a message called notice to let users know if the query didn't return any errors
                notice = ''
                if len(errors) == 0:
                    notice = f'No errors found matching the following filters: <br>Type: {filter_kwargs["type"] if "type" in filter_kwargs else None}<br>User:  {filter_kwargs["user"] if "user" in filter_kwargs else None},<br>Between dates {request.POST.get("error-by-daterange-start") if request.POST.get("error-by-daterange-start") != "" else "___"} and {request.POST.get("error-by-daterange-end") if request.POST.get("error-by-daterange-end") != "" else "___"}'
            if 'reduce_stored_errors' in request.POST:
                reduce_stored_errors()
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to view errors")
            except PermissionDenied as exc:
                new_error(exc, request.user)
            
        context = {
            'users':users,
            'errors':errors,
            'notice':notice,
            'is_operator':is_operator,
        }
        return render(request, 'error_handling/error_dashboard.html', context)

        
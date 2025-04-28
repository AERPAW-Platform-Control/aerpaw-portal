import datetime
from collections import defaultdict
from django.contrib import messages
from django.shortcuts import render
from django.urls import resolve, Resolver404
from django.utils import timezone
from functools import wraps

from portal.apps.error_handling.api.viewsets import AerpawErrorViewset
from portal.apps.error_handling.models import AerpawError, AerpawErrorGroup
from portal.apps.error_handling.error_dashboard import new_error_group
from portal.server.settings import MOCK_OPS


""" 
Write functions to handle specific errors
Determine how to handle when errors are redirected to error page vs shown on top of current page
    - Errors to redirect
        PermissionDenied
        NotFound
        Http404
    - Errors without redirect
        ValidationError
        AttributeError
        MethodNotAllowed


Built In Django messages levels
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40

CUSTOM Message levels
    PERMISSION_DENIED = 50
 """

def catch_all_errors_in_view(request, view, *args, **kwargs):
    start = timezone.now()
    view_repsonse = view(request, *args, **kwargs)
    errors = AerpawError.objects.filter(datetime__gt=start, user=request.user)
    return errors, view_repsonse

def get_view_name(view):
    if hasattr(view, '__self__') and hasattr(view.__self__, '__class__'):
        class_name = view.__self__.__class__.__name__
        method_name = view.__name__
        return f'{method_name}.{class_name}'
    else:
        view_name = view.__name__
        return view_name

def error_msg(request, error_types: list, error_group: AerpawErrorGroup) -> bool:
    error_page = False
    user = request.user
    ops_user = user.is_operator()

    # Get the correct variablesfor the environment. ie. Production vs Local Dev
    email = 'aerpaw-operations@ncsu.edu'
    error_dashboard_url = f'https://user-web-portal.aerpaw.ncsu.edu/error_handling/error_group_report/{error_group.id}'
    if MOCK_OPS:
        email = 'cjrober5@ncsu.edu'
        error_dashboard_url = f'http://127.0.0.1:8000/error_handling/error_group_report/{error_group.id}'

    ops_btn = f'<a class="btn btn-sm btn-outline-danger" href="{error_dashboard_url}">View Error Report</a>'
    user_btn = f'<br> If this error persists, please <a class="btn btn-sm btn-outline-danger" href="mailto:{email}?subject=Error#%20{error_group.id}">click here to email the Aerpaw Ops Team <i class="fa fa-paper-plane"></i></a>'
    if 'PermissionDenied' in error_types:
        error_page = True
        messages.add_message(request, 50, 'You do not have permission to view this page.')
    elif 'Http404' in error_types or 'DoesNotExist' in error_types or 'NotFound' in error_types:
        error_page = True
        if ops_user:
            messages.add_message(request, messages.INFO, f'The item you are looking for does not exist. {ops_btn}')
        else:
            messages.add_message(request, messages.INFO, 'The item you are looking for does not exist.')
    else:
        error_page = False
        if ops_user:
            messages.add_message(request, messages.INFO, f'Error# {error_group.id}: An Error has occured! {ops_btn}')
        else:
            messages.add_message(request, messages.INFO, f'Error# {error_group.id}: An Error has occured! {user_btn}')
    return error_page

def sort_errors_by_type(errors: list[AerpawError]):
    error_types = defaultdict(list)
    for error in errors:
        error_types[error.type].append(error)
    return error_types

def handle_error(view):

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        start = timezone.now()
        response = view(request, *args, **kwargs)
        errors = AerpawError.objects.filter(datetime__gt=start, user=request.user)
        user = request.user
        
        # Handle any errors that are present
        if errors.count() > 0:
            try:
                view_path = resolve(request.path_info).func
                view_path = f'{view_path.__module__}.{view_path.__name__}'  # Get the path to the view function
            except Resolver404:
                view_path = 'unknown'
            error_group = new_error_group(user, view_path, errors)      # Create a new AerpawErrorGroup Instance
            error_types = sort_errors_by_type(errors)                   # Sort all the caught errors by their exception type
            error_page = error_msg(request, error_types, error_group)   # Add the error message to the Django messages framework and get which template to return

            # If necessary, redirect to the custom error page
            # Usually for when the user should not view the template such as PermissionDenied
            # Otherwise return the view with the error message at the top
            if error_page:
                return render(request, 'error_handling/error_template.html')    
            return response
        
        # If there are no errors, then return the view
        else:
            return response

    return wrapper
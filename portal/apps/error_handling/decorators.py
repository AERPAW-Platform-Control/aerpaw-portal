import datetime
from django.contrib import messages
from django.shortcuts import render
from django.utils import timezone
from functools import wraps

from portal.apps.error_handling.models import AerpawError
from portal.apps.error_handling.error_dashboard import new_error

# Buitl In Django messages levels
# DEBUG = 10
# INFO = 20
# SUCCESS = 25
# WARNING = 30
# ERROR = 40

# CUSTOM Message levels
PERMISSION_DENIED = 50


def handle_error(view):

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        start = timezone.now()
        try:
            return view(request, *args, **kwargs)
        except Exception as e:
            # Catch the exception and display an error message to the user
            error_message = f"An error occurred: {str(e)}"

            # Get any errors caught throughout the function
            errors = AerpawError.objects.filter(datetime__gt=start, user=request.user)
            error_types = [error.type for error in errors]
            
            # Add the error message to the Django messages framework
            if 'PermissionDenied' in error_types:
                messages.add_message(request, PERMISSION_DENIED, 'You do not have permission to view this page')
                return render(request, 'error_handling/error_template.html')
            
            else:
                messages.error(request, error_message)
                return view(request, *args, **kwargs)  
        
    return wrapper
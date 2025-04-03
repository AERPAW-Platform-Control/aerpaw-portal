import datetime
from django.contrib import messages
from django.shortcuts import render
from functools import wraps

from portal.apps.error_handling.models import AerpawError

def handle_error(view):

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        start = datetime.datetime.now()
        try:
            print('Handling errors')
            return view(request, *args, **kwargs)
        except Exception as e:
            # Catch the exception and display an error message to the user
            error_message = f"An error occurred: {str(e)}"
            errors = AerpawError.objects.filter(datetime__gt=start, user=request.user)
            print(f'FOUND AN ERROR! {error_message}')
            print(f'Other errors= {errors}')
            error_types = [error.type for error in errors]
            

            # Add the error message to the Django messages framework
            #messages.error(request, error_message)
            
            # Optionally, log the exception for further debugging
            # For example: logging.exception("An error occurred in function %s", func.__name__)
            if 'PermissionDenied' in error_types:
                print('PERMISSION DENIED')
                return render(request, 'error_handling/error_template.html', {'message': 'You do not have permission to view this page'})
            return view(request, *args, **kwargs)  # Render an error page if needed
    return wrapper
from django.http import HttpRequest

from portal.apps.error_handling.api.viewsets import AerpawErrorViewset

def catch_exception(exc, request=None, user=None):
    if not request:
        request = HttpRequest()
        request.user = user if user else None
    return AerpawErrorViewset().create(request, exc)
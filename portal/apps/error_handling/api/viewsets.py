from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import MethodNotAllowed, NotFound, PermissionDenied, ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions


from portal.apps.error_handling.api.serializers import AerpawErrorSerializer
from portal.apps.error_handling.models import AerpawError

class AerpawErrorViewset(GenericViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = AerpawError.objects.all().order_by('user')
    serializer_class = AerpawErrorSerializer
    pass


from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import MethodNotAllowed, NotFound, PermissionDenied, ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions


from portal.apps.error_handling.api.serializers import AerpawErrorSerializer, AerpawThreadSerializer
from portal.apps.error_handling.models import AerpawError, AerpawThread

class AerpawErrorViewset(GenericViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = AerpawError.objects.all().order_by('user')
    serializer_class = AerpawErrorSerializer
    pass

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
            
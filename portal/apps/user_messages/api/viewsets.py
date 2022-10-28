from datetime import datetime, timezone

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from portal.apps.resources.api.serializers import ResourceSerializerDetail
from portal.apps.user_messages.api.serializers import UserMessageSerializerDetail, UserMessageSerializerList
from portal.apps.user_messages.models import AerpawUserMessage
from portal.apps.users.models import AerpawUser


class UserMessageViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Resource
    - paginated list
    - retrieve one
    - create
    - update
    - delete
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AerpawUserMessage.objects.all().order_by('-created')
    serializer_class = ResourceSerializerDetail

    def get_queryset(self):
        show_deleted = self.request.query_params.get('show_deleted', None)
        show_read = self.request.query_params.get('show_read', None)
        user_id = self.request.query_params.get('user_id', None)
        if str(show_deleted).casefold() == 'true':
            show_deleted = Q(is_deleted__in=[True, False])
        else:
            show_deleted = Q(is_deleted__in=[False])
        if str(show_read).casefold() == 'true':
            show_read = Q(is_read__in=[True, False])
        else:
            show_read = Q(is_read__in=[False])
        if user_id:
            q_filter = (Q(message_owner__id=user_id)) & show_read & show_deleted
        else:
            q_filter = Q(message_owner__id=self.request.user.id) & show_read & show_deleted

        queryset = AerpawUserMessage.objects.filter(
            q_filter
        ).order_by('-created').distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list user messages as paginated results
        - is_deleted             - bool
        - is_read                - bool
        - message_body           - string
        - message_id             - int
        - message_subject        - string
        - sent_by                - int:user_id
        - sent_date              - string

        @param show_deleted = user is_site_admin
        @param show_read = optional - default False
        @param user_id = user_id is user.id

        Permission:
        - user is_active
        """
        if request.user.is_active:
            # validate user message
            user_id = request.query_params.get('user_id', None)
            if user_id:
                # user_id must exist as valid user
                user = get_object_or_404(AerpawUser, pk=user_id)
                # user must be site admin or be the user themselves
                if not request.user.is_site_admin() and user.id != request.user.id:
                    raise PermissionDenied(
                        detail="PermissionDenied: unable to GET /requests list?user_id=...")
            # fetch response
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = UserMessageSerializerList(page, many=True)
            else:
                serializer = UserMessageSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'is_deleted': du.get('is_deleted'),
                        'is_read': du.get('is_read'),
                        'message_body': du.get('message_body'),
                        'message_id': du.get('message_id'),
                        'message_subject': du.get('message_subject'),
                        'sent_by': du.get('sent_by'),
                        'sent_date': str(du.get('sent_date')) if du.get('sent_date') else None
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /messages list")

    def create(self, request):
        """
        POST: create user message
        """
        raise MethodNotAllowed(method="POST: /messages")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: user message as detailed result
        - created          - string:sent_date
        - created_by       - string
        - id               - int:message_id
        - is_deleted       - bool
        - is_read          - bool
        - message_body     - string
        - message_owner    - int:user_id
        - message_subject  - string
        - modified         - string:last_modified_date
        - modified_by      - string
        - read_date        - string
        - received_by (fk) - array of int:user_id
        - sent_by (fk)     - int:user_id
        - uuid             - string

        Permission:
        - user is_active
        """
        user_message = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_active and user_message.message_owner == request.user:
            serializer = UserMessageSerializerDetail(user_message)
            du = dict(serializer.data)
            response_data = {
                'is_deleted': du.get('is_deleted'),
                'is_read': du.get('is_read'),
                'last_modified_by': AerpawUser.objects.get(username=du.get('last_modified_by')).id,
                'message_body': du.get('message_body'),
                'message_id': du.get('message_id'),
                'message_subject': du.get('message_subject'),
                'modified_date': str(du.get('modified_date')) if du.get('modified_date') else None,
                'received_by': du.get('received_by'),
                'read_date': str(du.get('read_date')) if du.get('read_date') else None,
                'sent_by': du.get('sent_by'),
                'sent_date': str(du.get('sent_date')) if du.get('sent_date') else None
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /messages/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: update existing message
        """
        raise MethodNotAllowed(method="PUT,PATCH: /messages/{0}".format(kwargs.get('pk')))

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update existing message
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: soft delete existing user message
        - is_deleted            - True
        - is_read               - True

        Permission:
        - user is_owner of message
        """
        user_message = get_object_or_404(self.queryset, pk=pk)
        if user_message.message_owner == request.user:
            user_message.is_deleted = True
            user_message.is_read = True
            user_message.modified = datetime.now(timezone.utc)
            user_message.modified_by = request.user.username
            user_message.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to DELETE /messages/{0} - user is not the owner".format(pk))

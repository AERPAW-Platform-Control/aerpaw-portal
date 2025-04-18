from datetime import datetime, timedelta, timezone
from uuid import uuid4

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from portal.apps.credentials.api.serializers import CredentialSerializerDetail, CredentialSerializerList
from portal.apps.credentials.api.utils import generate_rsa_2048_key
from portal.apps.credentials.models import CREDENTIAL_EXPIRY_DAYS, PublicCredentials
from portal.apps.error_handling.api.error_utils import catch_exception

# constants
PUBLIC_KEY_MIN_NAME_LEN = 5


class CredentialViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Credentials
    - created_date            - string
    - is_deleted              - boolean
    - is_expired:             - boolean
    - last_modified_by        - int
    - modified_date           - string
    - public_key_credential   - string
    - public_key_expiration   - int
    - public_key_id           - int
    - public_key_name         - string
    - user_id                 - int
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = PublicCredentials.objects.all().order_by('-created')
    serializer_class = CredentialSerializerDetail

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = PublicCredentials.objects.filter(
                is_deleted=False,
                owner__id=user_id
            ).order_by('-created').distinct()
        else:
            queryset = PublicCredentials.objects.filter(
                is_deleted=False
            ).order_by('-created').distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list of credentials as paginated results
        - created_date           - string
        - is_deleted             - bool
        - last_modified_by       - int
        - modified_date          - string
        - public_key_credential  - string
        - public_key_expiration  - int
        - public_key_id          - int
        - public_key_name        - string
        - user_id                - int

        Permission:
        - user is credential owner as identified by user_id
        - user is_operator
        """
        if request.user.id == int(request.query_params.get('user_id', 0)) or request.user.is_operator():
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = CredentialSerializerList(page, many=True)
            else:
                serializer = CredentialSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'public_key_credential': du.get('public_key_credential'),
                        'public_key_expiration': du.get('public_key_expiration'),
                        'public_key_id': du.get('public_key_id'),
                        'public_key_name': du.get('public_key_name'),
                        'user_id': du.get('user_id')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /credentials list")
            except PermissionDenied as exc:
                catch_exception(exc, request=request)

    def create(self, request):
        """
        POST: create new credential
        - public_key_credential  - string (optional - when not present a new key is generated)
        - public_key_name        - string (required)

        Permission:
        - user as_self
        """
        if request.user.is_active:
            # validate public_key_name
            public_key_name = request.data.get('public_key_name', None)
            if not public_key_name or len(public_key_name) < PUBLIC_KEY_MIN_NAME_LEN:
                try:
                    raise ValidationError(
                        detail="public_key_name:  must be at least {0} chars long".format(PUBLIC_KEY_MIN_NAME_LEN))
                except ValidationError as exc:
                    catch_exception(exc, request=request)
            # validate public_key_credential
            public_key_credential = request.data.get('public_key_credential', None)
            if not public_key_credential:
                new_key = generate_rsa_2048_key()
                public_key_credential = new_key.get('public_key')
            else:
                new_key = None
            # create public credential
            pub_key = PublicCredentials()
            pub_key.expiry_date = datetime.now(timezone.utc) + timedelta(days=CREDENTIAL_EXPIRY_DAYS)
            pub_key.name = public_key_name
            pub_key.public_credential = public_key_credential
            pub_key.uuid = uuid4()
            pub_key.owner = request.user
            pub_key.modified_by = request.user.username
            pub_key.save()
            if new_key:
                return self.retrieve(request, pk=pub_key.id, new_key=new_key)
            else:
                return self.retrieve(request, pk=pub_key.id)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to POST /credentials")
            except PermissionDenied as exc:
                catch_exception(exc, request=request)

    def retrieve(self, request, *args, **kwargs):
        """
        GET: credential as detailed result
        - created_date           - string
        - is_deleted             - bool
        - is_expired             - bool
        - last_modified_by       - int
        - modified_date          - string
        - public_key_credential  - string
        - public_key_expiration  - int
        - public_key_id          - int
        - public_key_name        - string
        - user_id                - int

        Permission:
        - user is credential owner OR
        - user is_operator
        """
        public_key = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user == public_key.owner or request.user.is_operator():
            serializer = CredentialSerializerDetail(public_key)
            is_expired = True if public_key.expiry_date < datetime.now(timezone.utc) else False
            du = dict(serializer.data)
            response_data = {
                'created_date': str(du.get('created_date')) if du.get('created_date') else None,
                'is_expired': is_expired,
                'last_modified_by': du.get('last_modified_by'),
                'modified_date': str(du.get('modified_date')) if du.get('modified_date') else None,
                'public_key_credential': du.get('public_key_credential'),
                'public_key_expiration': str(du.get('public_key_expiration')) if du.get(
                    'public_key_expiration') else None,
                'public_key_id': du.get('public_key_id'),
                'public_key_name': du.get('public_key_name'),
                'user_id': du.get('user_id')
            }
            if public_key.is_deleted:
                response_data.update({'is_deleted': du.get('is_deleted')})
            new_key = kwargs.get('new_key', None)
            if new_key:
                response_data.update({'private_key_credential': new_key.get('private_key')})
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /credentials/{0} details".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                catch_exception(exc, request=request)

    def update(self, request, *args, **kwargs):
        """
        PUT: update existing credential
        - public_key_name        - string

        Permission:
        - user is_credential_owner
        """
        pub_key = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user == pub_key.owner:
            modified = False
            # check for public_key_name
            if request.data.get('public_key_name', None):
                if len(request.data.get('public_key_name')) < PUBLIC_KEY_MIN_NAME_LEN:
                    try:
                        raise ValidationError(
                            detail="public_key_name:  must be at least {0} chars long".format(PUBLIC_KEY_MIN_NAME_LEN))
                    except ValidationError as exc:
                        catch_exception(exc, request=request)
                pub_key.name = request.data.get('public_key_name')
                modified = True
            # save if modified
            if modified:
                pub_key.modified_by = request.user.email
                pub_key.save()
            return self.retrieve(request, pk=pub_key.id)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to PUT/PATCH /credentials/{0} details".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                catch_exception(exc, request=request)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update existing credential
        - public_key_name        - string

        Permission:
        - user is_credential_owner
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: soft delete existing credential
        - is_deleted             - bool
        - is_expired             - bool

        Permission:
        - user is_credential_owner OR
        - user is_operator
        """
        pub_key = get_object_or_404(self.queryset, pk=pk)
        if request.user == pub_key.owner or request.user.is_operator():
            pub_key.is_deleted = True
            pub_key.expiry_date = datetime.now(timezone.utc)
            pub_key.modified_by = request.user.username
            pub_key.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to DELETE /credentials/{0}".format(pk))
            except PermissionDenied as exc:
                catch_exception(exc, request=request)

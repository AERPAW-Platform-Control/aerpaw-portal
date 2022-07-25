from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from portal.apps.operations.api.serializers import CanonicalNumberSerializerDetail, CanonicalNumberSerializerList
from portal.apps.operations.models import CanonicalNumber, get_current_canonical_number, set_current_canonical_number
from portal.apps.credentials.models import PublicCredentials
from portal.apps.credentials.api.serializers import CredentialSerializerDetail, CredentialSerializerList


class CredentialViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Credentials
    - TODO
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = PublicCredentials.objects.all().order_by('-created')
    serializer_class = CredentialSerializerDetail

    def get_queryset(self):
        experiment_id = self.request.query_params.get('experiment_id', None)
        user_id = self.request.query_params.get('user_id', None)
        if experiment_id and user_id:
            queryset = PublicCredentials.objects.filter(
                is_deleted=False,
                experiment__id=experiment_id,
                user__id=user_id
            ).order_by('-created').distinct()
        elif experiment_id:
            queryset = PublicCredentials.objects.filter(
                is_deleted=False,
                experiment__id=experiment_id
            ).order_by('-created').distinct()
        elif user_id:
            queryset = PublicCredentials.objects.filter(
                is_deleted=False,
                user__id=user_id
            ).order_by('-created').distinct()
        else:
            queryset = PublicCredentials.objects.filter(is_deleted=False).order_by('-created').distinct()
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
        - user is_operator
        """
        raise MethodNotAllowed(method="GET: list /canonical-number")
        # if request.user.is_operator():
        #     page = self.paginate_queryset(self.get_queryset())
        #     if page:
        #         serializer = CredentialSerializerList(page, many=True)
        #     else:
        #         serializer = CredentialSerializerList(self.get_queryset(), many=True)
        #     response_data = []
        #     for u in serializer.data:
        #         du = dict(u)
        #         response_data.append(
        #             {
        #                 'canonical_number': du.get('canonical_number'),
        #                 'canonical_number_id': du.get('canonical_number_id'),
        #                 'timestamp': du.get('timestamp')
        #             }
        #         )
        #     if page:
        #         return self.get_paginated_response(response_data)
        #     else:
        #         return Response(response_data)
        # else:
        #     raise PermissionDenied(
        #         detail="PermissionDenied: unable to GET /canonical-number list")

    def create(self, request):
        """
        POST: credentials cannot be created via the API
        """
        raise MethodNotAllowed(method="POST: /credentials")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: credential as detailed result
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
        - user is_operator
        """
        raise MethodNotAllowed(method="GET: /credentials details")
        # canonical_number = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        # if request.user.is_operator():
        #     serializer = CanonicalNumberSerializerDetail(canonical_number)
        #     du = dict(serializer.data)
        #     response_data = {
        #         'canonical_number': du.get('canonical_number'),
        #         'canonical_number_id': du.get('canonical_number_id'),
        #         'created_date': du.get('created_date'),
        #         'is_deleted': du.get('is_deleted'),
        #         'is_retired': du.get('is_retired'),
        #         'modified_date': du.get('modified_date'),
        #         'timestamp': du.get('timestamp')
        #     }
        #     return Response(response_data)
        # else:
        #     raise PermissionDenied(
        #         detail="PermissionDenied: unable to GET /credentials/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: credentials cannot be updated via the API
        """
        raise MethodNotAllowed(method="PUT/PATCH: /canonical-number/{int:pk}")

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: credentials cannot be updated via the API
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: credentials cannot be deleted via the API
        """
        raise MethodNotAllowed(method="DELETE: /credentials/{int:pk}")

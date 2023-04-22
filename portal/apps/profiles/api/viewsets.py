from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from portal.apps.profiles.api.serializers import UserProfileSerializerDetail
from portal.apps.profiles.models import AerpawUserProfile


class UserProfileViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Resource
    - paginated list
    - retrieve one
    - create
    - update
    - delete
    - experiments
    - projects
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AerpawUserProfile.objects.all().order_by('id')
    serializer_class = UserProfileSerializerDetail

    def list(self, request, *args, **kwargs):
        """
        GET: user projile cannot be listed via the API
        """
        raise MethodNotAllowed(method="GET: /users")

    def create(self, request):
        """
        POST: user profile cannot be created via the API
        """
        raise MethodNotAllowed(method="POST: /users")

    def retrieve(self, request, *args, **kwargs):
        """
        User Profile
        - access_token
        - employer
        - position
        - refresh_token
        - research_field

        Permission:
        - user id of user == pk requested
        """
        profile = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_active:
            serializer = UserProfileSerializerDetail(profile)
            du = dict(serializer.data)
            response_data = {
                'employer': du.get('employer') if du.get('employer') else None,
                'position': du.get('position') if du.get('position') else None,
                'research_field': du.get('research_field') if du.get('research_field') else None
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /users/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: update existing user profile
        - employer
        - position
        - research_field

        Permission:
        - user is_self
        """
        profile = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if str(request.user.profile.id) == str(kwargs.get('pk')):
            modified = False
            # check for employer
            if isinstance(request.data.get('employer'), str):
                profile.employer = request.data.get('employer', None)
                modified = True
            # check for position
            if isinstance(request.data.get('position'), str):
                profile.position = request.data.get('position', None)
                modified = True
            # check for research_field
            if isinstance(request.data.get('research_field'), str):
                profile.research_field = request.data.get('research_field', None)
                modified = True
            # save if modified
            if modified:
                profile.modified_by = request.user.email
                profile.save()
            return self.retrieve(request, pk=profile.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to PUT/PATCH /users/{0} details".format(kwargs.get('pk')))

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update existing user profile
        - employer
        - position
        - research_field

        Permission:
        - user is_self
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: user profile cannot be deleted via the API
        """
        raise MethodNotAllowed(method="DELETE: /users")

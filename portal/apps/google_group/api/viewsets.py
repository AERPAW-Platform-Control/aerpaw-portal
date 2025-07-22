from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from portal.apps.google_group.api.serializers import GoogleGroupMembershipSerializer
from portal.apps.google_group.models import GoogleGroupMembership


class GoogleGroupMembershipViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = GoogleGroupMembership.objects.all()
    serializer_class = GoogleGroupMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        membership = get_object_or_404(GoogleGroupMembership, user=request.user)
        serializer = GoogleGroupMembershipSerializer(membership)
        return Response(serializer.data)
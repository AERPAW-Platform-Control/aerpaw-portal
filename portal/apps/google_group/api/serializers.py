from rest_framework import serializers
from portal.apps.google_group.models import GoogleGroupMembership

class GoogleGroupMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model=GoogleGroupMembership
        fields='__all__'
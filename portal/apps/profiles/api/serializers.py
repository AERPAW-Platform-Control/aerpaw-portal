from rest_framework import serializers

from portal.apps.profiles.models import AerpawUserProfile


class UserProfileSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = AerpawUserProfile
        fields = ['employer', 'position', 'research_field']

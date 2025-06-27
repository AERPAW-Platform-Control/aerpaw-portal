from rest_framework import serializers

from portal.apps.error_handling.models import AerpawError

class AerpawErrorSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    datetime = serializers.DateTimeField(source='datetime')
    error_id = serializers.IntegerField(source='id', read_only=True)
    error_uuid = serializers.CharField(source='uuid')


    class Meta:
        model = AerpawError
        fields = ['error_id', 'user_id', 'datetime', 'type', 'traceback', 
                  'is_resovled', 'resolved_by', 'resovled_datetime', 'resolved_description', 
                  'message', 'error_uuid']

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
        
class AerpawThreadSerializer(serializers.ModelSerializer):
    thread_id = serializers.IntegerField(source='id', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    experiment_id = serializers.IntegerField(source='experiment.id', read_only=True)
    thread_start = serializers.DateTimeField(source='thread_start', read_only=True)
    thread_end = serializers.DateTimeField(source='thread_end')
    error_id = serializers.IntegerField(source='error.id')
    thread_uuid = serializers.CharField(source='uuid')

    class Meta:
        model = AerpawThread
        fields = ['thread_id', 'user_id', 'experiment_id', 'thread_start', 'thread_end', 'exit_code', 
                  'response', 'is_error', 'error_id', 'displayed', 'thread_uuid']
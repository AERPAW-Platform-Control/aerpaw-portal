from rest_framework import serializers

from portal.apps.user_requests.models import AerpawUserRequest


class UserRequestSerializerList(serializers.ModelSerializer):
    """
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - id (from Basemodel) - request_id
    - is_approved - bool
    - received_by (fk) - array of user_id
    - request_note - string
    - request_type - [experiment, project, role]
    - request_type_id (fk) - int
    - requested_by (fk) - user_id - same as "created_by"
    - requested_date - UTC - same as "created"
    """
    request_id = serializers.IntegerField(source='id', read_only=True)
    requested_date = serializers.DateTimeField(source='created')

    class Meta:
        model = AerpawUserRequest
        fields = ['is_approved', 'received_by', 'request_id', 'request_note', 'request_type', 'request_type_id',
                  'requested_by', 'requested_date']


class UserRequestSerializerDetail(serializers.ModelSerializer):
    """
    - completed_by (fk) - user_id
    - completed_date - UTC
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - id (from Basemodel) - request_id
    - is_approved - bool
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - received_by (fk) - array of user_id
    - request_note - string
    - request_type - [experiment, project, role]
    - request_type_id (fk) - int
    - requested_by (fk) - user_id - same as "created_by"
    - requested_date - UTC - same as "created"
    - response_date - UTC
    - response_note - string
    - uuid
    """
    last_modified_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')
    request_id = serializers.IntegerField(source='id', read_only=True)
    requested_date = serializers.DateTimeField(source='created')

    class Meta:
        model = AerpawUserRequest
        fields = ['completed_by', 'completed_date', 'is_approved', 'last_modified_by', 'modified_date', 'received_by',
                  'request_id', 'request_note', 'request_type', 'request_type_id', 'requested_by', 'requested_date',
                  'response_date', 'response_note']

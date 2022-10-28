from rest_framework import serializers

from portal.apps.user_messages.models import AerpawUserMessage


class UserMessageSerializerList(serializers.ModelSerializer):
    """
    - created          - string:sent_date
    - created_by       - string
    - id               - int:message_id
    - is_deleted       - bool
    - is_read          - bool
    - message_body     - string
    - message_subject  - string
    - modified         - string:last_modified_date
    - modified_by      - string
    - read_date        - string
    - received_by (fk) - array of int:user_id
    - sent_by (fk)     - int:user_id
    - uuid             - string
    """
    message_id = serializers.IntegerField(source='id', read_only=True)
    sent_date = serializers.DateTimeField(source='created')

    class Meta:
        model = AerpawUserMessage
        fields = ['is_deleted', 'is_read', 'message_body', 'message_id', 'message_subject', 'sent_by', 'sent_date']


class UserMessageSerializerDetail(serializers.ModelSerializer):
    """
    - created          - string:sent_date
    - created_by       - string
    - id               - int:message_id
    - is_deleted       - bool
    - is_read          - bool
    - message_body     - string
    - message_subject  - string
    - modified         - string:last_modified_date
    - modified_by      - string
    - read_date        - string
    - received_by (fk) - array of int:user_id
    - sent_by (fk)     - int:user_id
    - uuid             - string
    """
    last_modified_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')
    message_id = serializers.IntegerField(source='id', read_only=True)
    sent_date = serializers.DateTimeField(source='created')

    class Meta:
        model = AerpawUserMessage
        fields = ['is_deleted', 'is_read', 'last_modified_by', 'message_body', 'message_id', 'message_subject',
                  'modified_date', 'received_by', 'read_date', 'sent_by', 'sent_date']

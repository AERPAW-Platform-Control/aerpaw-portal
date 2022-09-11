from rest_framework import serializers

from portal.apps.experiments.models import ExperimentFile


class ExperimentFileSerializerList(serializers.ModelSerializer):
    """
    file_id              - int
    file_location        - string
    file_name            - string
    file_notes           - string
    file_type            - enum["ip_list", "ovpn"]
    is_active            - bool
    is_deleted           - bool
    """
    file_id = serializers.IntegerField(source='id')

    class Meta:
        model = ExperimentFile
        fields = ['file_id', 'file_location', 'file_name', 'file_notes', 'file_type', 'is_active', 'is_deleted']


class ExperimentFileSerializerDetail(serializers.ModelSerializer):
    """
    created_by           - string
    created_date         - string
    file_id              - int
    file_location        - string
    file_name            - string
    file_notes           - string
    file_type            - enum["ip_list", "ovpn"]
    is_active            - bool
    is_deleted           - bool
    last_modified_by     - string
    modified_date        - string
    """
    created_date = serializers.DateTimeField(source='created')
    file_id = serializers.IntegerField(source='id')
    last_modified_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')

    class Meta:
        model = ExperimentFile
        fields = ['created_by', 'created_date', 'file_id', 'file_location', 'file_name', 'file_notes', 'file_type',
                  'is_active', 'is_deleted', 'last_modified_by', 'modified_date']

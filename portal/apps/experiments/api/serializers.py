from rest_framework import serializers

from portal.apps.experiments.models import AerpawExperiment, CanonicalExperimentResource, ExperimentSession, \
    OpsSession, UserExperiment


class UserExperimentSerializer(serializers.ModelSerializer):
    experiment_id = serializers.IntegerField(source='experiment.id')
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = UserExperiment
        fields = ['granted_by', 'granted_date', 'experiment_id', 'id', 'user_id']


class ExperimentSerializerList(serializers.ModelSerializer):
    canonical_number = serializers.IntegerField(source='canonical_number.canonical_number')
    created_date = serializers.DateTimeField(source='created')
    experiment_id = serializers.IntegerField(source='id', read_only=True)
    experiment_uuid = serializers.CharField(source='uuid')

    class Meta:
        model = AerpawExperiment
        fields = ['canonical_number', 'created_date', 'description', 'experiment_creator', 'experiment_id',
                  'experiment_uuid', 'experiment_state', 'is_canonical', 'is_retired', 'name', 'project_id']


class ExperimentSerializerDetail(serializers.ModelSerializer):
    canonical_number = serializers.IntegerField(source='canonical_number.canonical_number')
    created_date = serializers.DateTimeField(source='created')
    experiment_id = serializers.IntegerField(source='id', read_only=True)
    experiment_uuid = serializers.CharField(source='uuid')
    last_modified_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')
    project_id = serializers.IntegerField(source='project.id')
    experiment_membership = UserExperimentSerializer(source='userexperiment_set', many=True)

    class Meta:
        model = AerpawExperiment
        fields = ['canonical_number', 'created_date', 'description', 'experiment_creator', 'experiment_flags',
                  'experiment_id', 'experiment_uuid', 'experiment_membership', 'experiment_state', 'is_canonical',
                  'is_emulation_required', 'is_retired', 'last_modified_by', 'modified_date', 'name', 'project_id',
                  'resources', 'resources_locked']


class ExperimentSerializerState(serializers.ModelSerializer):
    experiment_id = serializers.IntegerField(source='id', read_only=True)
    experiment_state = serializers.DateTimeField(source='state')
    experiment_uuid = serializers.CharField(source='uuid')

    class Meta:
        model = AerpawExperiment
        fields = ['experiment_flags', 'experiment_id', 'experiment_state', 'experiment_uuid']


class ExperimentSessionSerializerList(serializers.ModelSerializer):
    """
    Experiment Session List
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - * ended_by
    - * ended_date_time
    - * experiment
    - * id (from Basemodel)
    - * is_active
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - * session_type
    - * start_date_time
    - * started_by
    - uuid
    """
    experiment_id = serializers.IntegerField(source='experiment.id')
    session_id = serializers.IntegerField(source='id')

    class Meta:
        model = ExperimentSession
        fields = ['end_date_time', 'ended_by', 'experiment_id', 'is_active', 'session_id', 'session_type',
                  'start_date_time', 'started_by']


class ExperimentSessionSerializerDetail(serializers.ModelSerializer):
    """
    Experiment Session Detail
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - ended_by
    - ended_date_time
    - experiment
    - id (from Basemodel)
    - is_active
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - session_type
    - start_date_time
    - started_by
    - uuid
    """
    created_time = serializers.DateTimeField(source='created')
    experiment_id = serializers.IntegerField(source='experiment.id')
    modified_time = serializers.DateTimeField(source='modified')
    session_id = serializers.IntegerField(source='id')

    class Meta:
        model = ExperimentSession
        fields = ['created_by', 'created_time', 'end_date_time', 'ended_by', 'experiment_id', 'is_active',
                  'modified_by', 'modified_time', 'session_id', 'session_type', 'start_date_time', 'started_by']


class OpsSessionSerializerList(serializers.ModelSerializer):
    """
    Ops Session - created by Aerpaw Ops team to manually manage sessions 
    - *description (an explanation to be emailed to experimenters describing success status)
    - *scheduled_by
    - *scheduled_created_on (date the scheduled date_time was created)
    - scheduled_active_date (date the session will occur)
    - *canceled_by
    - *canceled
    - *session_state (the place the session is currently in the session workflow)
    - *is_success

    Inherits from Experiment Session
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - *ended_by
    - *ended_date_time
    - *experiment
    - *id (from Basemodel)
    - *is_active
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - *session_type
    - *start_date_time
    - *started_by
    - uuid
    """
    experiment_id = serializers.IntegerField(source='experiment.id')
    session_id = serializers.IntegerField(source='id')

    class Meta:
        model = OpsSession
        fields = ['end_date_time', 'ended_by', 'experiment_id', 'is_active', 'scheduled_active_date', 'session_id', 'session_state', 
                  'session_type', 'start_date_time', 'started_by']



class OpsSessionSerializerDetail(serializers.ModelSerializer):
    canceled_date = serializers.DateTimeField(source='canceled')
    created_by = serializers.CharField(source='created_by')
    created_date = serializers.DateTimeField(source='created')
    ended_date = serializers.DateTimeField(source='ended_date_time')
    ended_by = serializers.CharField(source='ended_by')
    experiment_id = serializers.IntegerField(source='experiment.id')
    modifed_date = serializers.DateTimeField(source='modified')
    modified_by = serializers.CharField(source='modified_by')
    ops_session_id = serializers.IntegerField(source='id')
    scheduled_active_date = serializers.DateTimeField(source='scheduled_active_date') # The actual date the session will become active
    scheduled_created_on = serializers.DateTimeField(source='scheduled_created_on') # The date the scheduled date was planned/created-on

    class Meta:
        model = OpsSession
        fields = ['canceled_by', 'canceled_date', 'created_by', 'created_date', 'ended_by', 'ended_date',  'experiment_id', 'description',
                   'is_active', 'is_success', 'modified_by', 'modifed_date', 'ops_session_id',  
                   'scheduled_active_date', 'scheduled_by', 'scheduled_created_on', 'session_state', 'session_type'
                    ]

class CanonicalExperimentResourceSerializer(serializers.ModelSerializer):
    canonical_experiment_resource_id = serializers.IntegerField(source='id')
    experiment_id = serializers.IntegerField(source='experiment.id')
    resource_id = serializers.IntegerField(source='resource.id')

    class Meta:
        model = CanonicalExperimentResource
        fields = ['canonical_experiment_resource_id', 'experiment_id', 'experiment_node_number', 'node_display_name',
                  'node_type', 'node_uhd', 'node_vehicle', 'resource_id']

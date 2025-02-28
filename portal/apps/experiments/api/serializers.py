from rest_framework import serializers

from portal.apps.experiments.models import AerpawExperiment, CanonicalExperimentResource, OnDemandSession, \
    ScheduledSession, UserExperiment


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
                  'resources', 'resources_locked', 'members_locked']


class ExperimentSerializerState(serializers.ModelSerializer):
    experiment_id = serializers.IntegerField(source='id', read_only=True)
    experiment_state = serializers.DateTimeField(source='state')
    experiment_uuid = serializers.CharField(source='uuid')

    class Meta:
        model = AerpawExperiment
        fields = ['experiment_flags', 'experiment_id', 'experiment_state', 'experiment_uuid']


class OnDemandSessionSerializerList(serializers.ModelSerializer):
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
        model = OnDemandSession
        fields = ['end_date_time', 'ended_by', 'experiment_id', 'is_active', 'session_id', 'session_type',
                  'start_date_time', 'started_by']


class OnDemandSessionSerializerDetail(serializers.ModelSerializer):
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
        model = OnDemandSession
        fields = ['created_by', 'created_time', 'end_date_time', 'ended_by', 'experiment_id', 'is_active',
                  'modified_by', 'modified_time', 'session_id', 'session_type', 'start_date_time', 'started_by']


class ScheduledSessionSerializerList(serializers.ModelSerializer):
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
        model = ScheduledSession
        fields = ['end_date_time', 'ended_by', 'experiment_id', 'is_active', 'scheduled_start', 'scheduled_end', 'session_id', 'session_state', 
                  'session_type', 'start_date_time', 'started_by']


class ScheduledSessionSerializerDetail(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(source='created')
    experiment_id = serializers.IntegerField(source='experiment.id')
    modified_time = serializers.DateTimeField(source='modified')    
    session_id = serializers.IntegerField(source='id')

    class Meta:
        model = ScheduledSession
        fields = ['created_by', 'created_time', 'description', 'ended_by', 'end_date_time',  'experiment_id',
                   'is_active', 'modified_by', 'modified_time', 'session_id',  
                   'session_type', 'start_date_time', 'started_by'
                    ]


class CanonicalExperimentResourceSerializer(serializers.ModelSerializer):
    canonical_experiment_resource_id = serializers.IntegerField(source='id')
    experiment_id = serializers.IntegerField(source='experiment.id')
    resource_id = serializers.IntegerField(source='resource.id')
    resource_hostname = serializers.CharField(source='resource.location')

    class Meta:
        model = CanonicalExperimentResource
        fields = ['canonical_experiment_resource_id', 'experiment_id', 'experiment_node_number', 'node_display_name',
                  'node_type', 'node_uhd', 'node_vehicle', 'resource_id', 'resource_hostname']

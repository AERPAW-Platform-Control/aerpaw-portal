from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from portal.apps.experiment_files.models import ExperimentFile
from portal.apps.mixins.models import AuditModelMixin, BaseModel, BaseTimestampModel
from portal.apps.operations.models import CanonicalNumber
from portal.apps.projects.models import AerpawProject
from portal.apps.resources.models import AerpawResource
from portal.apps.users.models import AerpawUser


class AerpawExperiment(BaseModel, AuditModelMixin, models.Model):
    """
    Experiment
    - canonical_number
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - description
    - emulation_required - bool
    - experiment_files - array of fk to ExperimentFile
    - experiment_flags
    - experiment_membership
    - experiment_state
    - id (from Basemodel)
    - is_canonical
    - is_deleted
    - is_retired
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - name
    - project
    - resources
    - uuid
    """

    class ExperimentState(models.TextChoices):
        ACTIVE_DEVELOPMENT = 'active_development', _('Active Development')
        ACTIVE_EMULATION = 'active_emulation', _('Active Emulation')
        ACTIVE_SANDBOX = 'active_sandbox', _('Active Sandbox')
        ACTIVE_TESTBED = 'active_testbed', _('Active Testbed')
        SAVING_DEVELOPMENT = 'saving_development', _('Saving Development')
        SAVING_SANDBOX = 'saving_sandbox', _('Saving Sandbox')
        SAVED = 'saved', _('Saved')
        WAIT_DEVELOPMENT_DEPLOY = 'wait_development_deploy', _('Wait Development Deploy')
        WAIT_EMULATION_DEPLOY = 'wait_emulation_deploy', _('Wait Emulation Deploy')
        WAIT_EMULATION_SCHEDULE = 'wait_emulation_schedule', _('Wait Emulation Schedule')
        WAIT_SANDBOX_DEPLOY = 'wait_sandbox_deploy', _('Wait Sandbox Deploy')
        WAIT_TESTBED_DEPLOY = 'wait_testbed_deploy', _('Wait Testbed Deploy')
        WAIT_TESTBED_SCHEDULE = 'wait_testbed_schedule', _('Wait Testbed Schedule')

    canonical_number = models.ForeignKey(
        CanonicalNumber,
        related_name='canonical_experiment_number',
        on_delete=models.PROTECT
    )
    description = models.TextField(blank=False, null=False)
    experiment_creator = models.ForeignKey(
        AerpawUser,
        related_name='experiment_creator',
        on_delete=models.PROTECT
    )
    experiment_files = models.ManyToManyField(
        ExperimentFile,
        related_name='experiment_files'
    )
    experiment_flags = models.CharField(max_length=3, default='000')
    experiment_membership = models.ManyToManyField(
        AerpawUser,
        related_name='experiment_membership',
        through='UserExperiment',
        through_fields=('experiment', 'user')
    )
    experiment_state = models.CharField(
        max_length=255,
        choices=ExperimentState.choices,
        default=ExperimentState.SAVED
    )
    is_canonical = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_emulation_required = models.BooleanField(default=True)
    is_retired = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    project = models.ForeignKey(
        AerpawProject,
        related_name='experiment_project',
        on_delete=models.PROTECT
    )
    resources = models.ManyToManyField(
        AerpawResource,
        related_name='experiment_resources'
    )
    resources_locked = models.BooleanField(default=False)
    members_locked = models.BooleanField(default=False)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        verbose_name = 'AERPAW Experiment'

    def __str__(self):
        return self.name

    def is_creator(self, user: AerpawUser) -> bool:
        return user == self.experiment_creator

    def is_member(self, user: AerpawUser) -> bool:
        return UserExperiment.objects.filter(
            user=user, experiment=self).exists()

    def experiment_members(self) -> AerpawUser:
        return AerpawUser.objects.filter(
            id__in=UserExperiment.objects.filter(experiment=self).values_list('user_id', flat=True)
        ).order_by('display_name')

    def state(self):
        return self.experiment_state


class UserExperiment(BaseModel, models.Model):
    """
    User-Experiment relationship
    - experiment_id
    - granted_by
    - granted_date
    - id (from Basemodel)
    - user_id
    """

    experiment = models.ForeignKey(AerpawExperiment, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(AerpawUser, related_name='experiment_granted_by', on_delete=models.CASCADE)
    granted_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(AerpawUser, related_name='experiment_user', on_delete=models.CASCADE)


class OnDemandSession(BaseModel, AuditModelMixin, models.Model):
    """
    Experiment Session
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

    class SessionType(models.TextChoices):
        DEVELOPMENT = 'development', _('Development')
        EMULATION = 'emulation', _('Emulation')
        SANDBOX = 'sandbox', _('Sandbox')
        TESTBED = 'testbed', _('Testbed')

    ended_by = models.ForeignKey(
        AerpawUser,
        related_name='session_ended_by',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    end_date_time = models.DateTimeField(blank=True, null=True)
    experiment = models.ForeignKey(
        AerpawExperiment,
        related_name='session_experiment',
        on_delete=models.PROTECT
    )
    is_active = models.BooleanField(default=True)
    session_type = models.CharField(
        max_length=255,
        choices=SessionType.choices,
        default=SessionType.DEVELOPMENT
    )
    started_by = models.ForeignKey(
        AerpawUser,
        related_name='session_started_by',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    start_date_time = models.DateTimeField(blank=True, null=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)


class ScheduledSession(OnDemandSession, models.Model):
    """ 
    Scheduled Session  
    - description (an explanation to be emailed to experimenters describing success status)
    - scheduled_by
    - scheduled_created_on (date the scheduled date_time was created)
    - scheduled_active_date (date the session will occur)
    - canceled_by
    - canceled
    - session_state (the place the session is currently in the session workflow)
    - is_success

    Inherits from On Demand Session
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

    Scheduled Session Work Flow
    • wait_schedule -> scheduled -> started -> completed •
    """

    class SessionStateChoices(models.TextChoices):
        CANCELED = 'canceled', _('Canceled')
        COMPLETED = 'completed', _('Completed')
        SCHEDULED = 'scheduled', _('Scheduled')
        STARTED = 'started', _('Started')
        WAIT_SCHEDULE = 'wait_schedule', _('Wait_Schedule')

        
    description = models.TextField(blank=True)
    is_success = models.BooleanField(default=False)
    scheduled_start = models.DateTimeField(blank=True, null=True) # The date the session will turn active
    scheduled_end = models.DateTimeField(blank=True, null=True) # The date the session will turn inactive
    scheduled_by = models.ForeignKey(
        AerpawUser,
        related_name='session_scheduled_by',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    scheduled_created_on = models.DateTimeField(blank=True, null=True) # The date when the scheduled_active_date was created
    session_state = models.CharField(
        max_length=255,
        choices=SessionStateChoices.choices,
        default=SessionStateChoices.WAIT_SCHEDULE
    )


class CanonicalExperimentResource(BaseModel, BaseTimestampModel, models.Model):
    """
    Canonical Experiment Resource
    - created (from BaseTimestampModel)
    - experiment
    - experiment_node_number
    - id (from Basemodel)
    - modified (from BaseTimestampModel)
    - node_display_name
    - node_type
    - node_uhd
    - node_vehicle
    - resource
    - uuid
    """

    class NodeType(models.TextChoices):
        AFRN = 'afrn', _('AFRN')
        APRN = 'aprn', _('APRN')
        ACN = 'acn', _('ACN')

    class NodeUhd(models.TextChoices):
        FOUR_THREE = '4.3', _('4.3')

    class NodeVehicle(models.TextChoices):
        VEHICLE_UAV = 'vehicle_uav', _('Vehicle UAV')
        VEHICLE_UGV = 'vehicle_ugv', _('Vehicle UGV')
        VEHICLE_OTHER = 'vehicle_other', _('Vehicle Other')
        VEHICLE_NONE = 'vehicle_none', _('Vehicle None')

    experiment = models.ForeignKey(
        AerpawExperiment,
        related_name='cer_experiment',
        on_delete=models.PROTECT
    )
    experiment_node_number = models.IntegerField(default=1)
    node_display_name = models.CharField(max_length=255, blank=True, null=True)
    node_type = models.CharField(
        max_length=255,
        choices=NodeType.choices,
        default=NodeType.AFRN
    )
    node_uhd = models.CharField(
        max_length=255,
        choices=NodeUhd.choices,
        default=NodeUhd.FOUR_THREE
    )
    node_vehicle = models.CharField(
        max_length=255,
        choices=NodeVehicle.choices,
        default=NodeVehicle.VEHICLE_NONE if node_type==NodeType.AFRN else NodeVehicle.VEHICLE_UAV
    )
    resource = models.ForeignKey(
        AerpawResource,
        related_name='cer_resource',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)


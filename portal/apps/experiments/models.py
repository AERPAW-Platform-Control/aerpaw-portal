from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fsm import transition, FSMIntegerField

from portal.apps.mixins.models import AuditModelMixin, BaseModel, BaseTimestampModel
from portal.apps.operations.models import CanonicalNumber
from portal.apps.projects.models import AerpawProject
from portal.apps.resources.models import AerpawResource
from portal.apps.users.models import AerpawUser

import logging

logger = logging.getLogger(__name__)

class AerpawExperiment(BaseModel, AuditModelMixin, models.Model):
    """
    Experiment
    - canonical_number
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - description
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

    #class ExperimentState(models.TextChoices):
        #ACTIVE_DEVELOPMENT = 'active_development', _('Active Development')
        #ACTIVE_EMULATION = 'active_emulation', _('Active Emulation')
        #ACTIVE_SANDBOX = 'active_sandbox', _('Active Sandbox')
        #ACTIVE_TESTBED = 'active_testbed', _('Active Testbed')
        #SAVED = 'saved', _('Saved')
        #WAIT_DEVELOPMENT_DEPLOY = 'wait_development_deploy', _('Wait Development Deploy')
        #WAIT_EMULATION_DEPLOY = 'wait_emulation_deploy', _('Wait Emulation Deploy')
        #WAIT_SANDBOX_DEPLOY = 'wait_sandbox_deploy', _('Wait Sandbox Deploy')
        #WAIT_TESTBED_DEPLOY = 'wait_testbed_deploy', _('Wait Testbed Deploy')

    STATE_SAVED = 0
    STATE_WAIT_DEVELOPMENT_DEPLOY = 1
    STATE_ACTIVE_DEVELOPMENT = 2
    STATE_WAIT_EMULATION_DEPLOY = 3
    STATE_ACTIVE_EMULATION = 4

    STATE_WAIT_SANDBOX_DEPLOY = 5
    STATE_ACTIVE_SANDBOX = 6
    STATE_WAIT_TESTBED_DEPLOY  = 7
    STATE_ACTIVE_TESTBED = 8

    STATE_CHOICES = (
        (STATE_SAVED, 'Saved'),
        (STATE_WAIT_DEVELOPMENT_DEPLOY, 'Wait Development Deploy'),
        (STATE_ACTIVE_DEVELOPMENT, 'Active Development'),
        (STATE_WAIT_EMULATION_DEPLOY, 'Wait Emulation Deploy'),
        (STATE_ACTIVE_EMULATION, 'Active Emulation'),
        (STATE_WAIT_SANDBOX_DEPLOY, 'Wait Sandbox Deploy'),
        (STATE_ACTIVE_SANDBOX , 'deploying'),
        (STATE_WAIT_TESTBED_DEPLOY, 'Wait Testbed Deploy'),
        (STATE_ACTIVE_TESTBED, 'submitted'),
    )

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
    experiment_membership = models.ManyToManyField(
        AerpawUser,
        related_name='experiment_membership',
        through='UserExperiment',
        through_fields=('experiment', 'user')
    )
    #experiment_state = models.CharField(
    #    max_length=255,
    #    choices=STATE_CHOICES,
    #    default=STATE_WAIT_DEVELOPMENT_DEPLOY
    #)
    is_canonical = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
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
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    experiment_state = FSMIntegerField(default=0, blank=True, null=True, choices=STATE_CHOICES)

    @transition(field=experiment_state, source=STATE_SAVED, target=STATE_WAIT_DEVELOPMENT_DEPLOY)
    def provision_development(self):
        logger.warning("[{}] Experiment.state : {} -> {}".format(self.name, self.state, AerpawExperiment.STATE_WAIT_DEVELOPMENT_DEPLOY))

    @transition(field=experiment_state, source=STATE_WAIT_DEVELOPMENT_DEPLOY, target=STATE_ACTIVE_DEVELOPMENT)
    def deploy_development(self):
        logger.warning("[{}] Experiment.state : {} -> {}".format(self.name, self.state, AerpawExperiment.STATE_ACTIVE_DEVELOPMENT))

    @transition(field=experiment_state, source=STATE_ACTIVE_DEVELOPMENT, target=STATE_WAIT_TESTBED_DEPLOY)
    def submit_testbed(self):
        logger.warning("[{}] Experiment.state : {} -> {}".format(self.name, self.state, AerpawExperiment.STATE_WAIT_TESTBED_DEPLOY))

    @transition(field=experiment_state, source=STATE_WAIT_TESTBED_DEPLOY, target=STATE_ACTIVE_TESTBED)
    def deploy_testbed(self):
        logger.warning("[{}] Experiment.state : {} -> {}".format(self.name, self.state, AerpawExperiment.STATE_ACTIVE_TESTBED))

    @transition(field=experiment_state, source=[STATE_SAVED, STATE_WAIT_DEVELOPMENT_DEPLOY, STATE_ACTIVE_DEVELOPMENT, STATE_WAIT_TESTBED_DEPLOY, STATE_ACTIVE_TESTBED], target=STATE_SAVED)
    def idle(self):
        logger.warning("[{}] Experiment.state : {} -> {}".format(self.name, self.state, AerpawExperiment.STATE_SAVED))

    deployment_bn = models.IntegerField(blank=True, null=True) # not being used
    message = models.TextField(blank=True, null=True) # message from system/ops
    submit_notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'AERPAW Experiment'

    def __str__(self):
        return self.name

    def status(self):
        return dict(self.STATE_CHOICES).get(int(self.experiment_state))

    def can_initiate(self):
        if int(self.experiment_state) == AerpawExperiment.STATE_SAVED:
            return True
        else:
            return False

    def can_terminate(self):
        if int(self.experiment_state) != AerpawExperiment.STATE_SAVED:
            return True
        else:
            return False

    def can_snapshot(self):
        if int(self.experiment_state) == AerpawExperiment.STATE_ACTIVE_DEVELOPMENT:
            return True
        else:
            return False

    def can_submit(self):
        if int(self.experiment_state) == AerpawExperiment.STATE_ACTIVE_DEVELOPMENT:
            return True
        else:
            return False

    def __str__(self):
        return self.name

    def is_creator(self, user: AerpawUser) -> bool:
        return user == self.experiment_creator

    def is_member(self, user: AerpawUser) -> bool:
        return UserExperiment.objects.filter(
            user=user, experiment=self).exists()

    def experiment_members(self) -> [AerpawUser]:
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


class ExperimentSession(BaseModel, BaseTimestampModel, models.Model):
    """
    Experiment Session
    - created (from BaseTimestampModel)
    - ended_by
    - ended_date_time
    - experiment
    - id (from Basemodel)
    - modified (from BaseTimestampModel)
    - session_type
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
    session_type = models.CharField(
        max_length=255,
        choices=SessionType.choices,
        default=SessionType.DEVELOPMENT
    )
    started_by = models.ForeignKey(
        AerpawUser,
        related_name='session_started_by',
        on_delete=models.PROTECT
    )
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    def __str__(self):
        return str(self.id) + ";" + str(self.started_by.id)
    
    def is_creator(self, user: AerpawUser) -> bool:
        #return user == self.started_by
        return True

class CanonicalExperimentResource(BaseModel, BaseTimestampModel, models.Model):
    """
    Canonical Experiment Resource
    - created (from BaseTimestampModel)
    - experiment
    - experiment_node_number
    - id (from Basemodel)
    - modified (from BaseTimestampModel)
    - node_type
    - node_uhd
    - node_vehicle
    - resource
    - uuid
    """

    class NodeType(models.TextChoices):
        AFRN = 'afrn', _('AFRN')
        APRN = 'aprn', _('APRN')

    class NodeUhd(models.TextChoices):
        ONE_THREE_THREE = '1.3.3', _('1.3.3')
        ONE_FOUR = '1.4', _('1.4')

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
    node_type = models.CharField(
        max_length=255,
        choices=NodeType.choices,
        default=NodeType.AFRN
    )
    node_uhd = models.CharField(
        max_length=255,
        choices=NodeUhd.choices,
        default=NodeUhd.ONE_THREE_THREE
    )
    node_vehicle = models.CharField(
        max_length=255,
        choices=NodeVehicle.choices,
        default=NodeVehicle.VEHICLE_NONE
    )
    resource = models.ForeignKey(
        AerpawResource,
        related_name='cer_resource',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

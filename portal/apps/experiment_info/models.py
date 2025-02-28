from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from portal.apps.mixins.models import BaseModel, BaseTimestampModel
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.resources.models import AerpawResource
from portal.apps.users.models import AerpawUser


# Create your models here.
class ExperimentFormData(BaseModel, BaseTimestampModel, models.Model):
    """ 
    id - from BaseModel
    created - datetime from BaseTimestampModel
    modified - datetime from BaseTimestampModel
    experiment - forgien key
    title - charfield: experiment title
    host_institution - charfield
    lead_experimenter - charfield
    lead_email - email
    uuid
    """

    class ExperimentLocation(models.TextChoices):
        LAKE_WHEELER = 'lake_wheeler', _('Lake Wheeler')
        CENTENNIAL_CAMPUS = 'centennial_campus', _('Centennial Campus')
        EMULATION = 'emulation', _('Emulation')
        SANDBOX = 'sandbox', _('Sandbox')
        TEST_BED = 'test_bed', _('Both LW and CC')
        OTHER = 'other', _('Other')

    class ExperimentType(models.TextChoices):
        CANONICAL = 'canonical', _('Canonical')
        NON_CANONICAL = 'non_canonical', _('Non-Canonical')
        CUSTOM = 'custom', _('Custom')

    class ExtendedBoolean(models.TextChoices):
        YES = 'yes', _('Yes')
        NO = 'no', _('No')
        NOT_SURE = 'not_sure', _('Not Sure')
    
    old_form_row_number = models.SmallIntegerField(blank=True, null=True)
    experiment_type = models.CharField(max_length=25,  choices=ExperimentType.choices, default=ExperimentType.CANONICAL)
    title = models.CharField(max_length=255)
    host_institution = models.CharField(max_length=255, blank=True, null=True)
    lead_experimenter = models.CharField(max_length=255, blank=True, null=True)
    lead_email = models.EmailField()
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)
    experiment = models.ForeignKey(AerpawExperiment, on_delete=models.CASCADE, blank=True, null=True)
    is_urgent = models.BooleanField(blank=True, null=True)
    sponsored_project = models.CharField(max_length=255, blank=True, null=True)
    grant_number = models.CharField(max_length=255, blank=True, null=True)
    keywords = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, choices=ExperimentLocation.choices, blank=True)
    is_shared = models.CharField(max_length=10, choices=ExtendedBoolean.choices, default=ExtendedBoolean.NOT_SURE)
    public_url = models.URLField(blank=True, null=True)
    goal = models.TextField()
    vehicle_behavior = models.TextField()
    description = models.TextField(blank=True, null=True)
    byod_hardware = models.TextField(blank=True, null=True)
    byod_software = models.TextField(blank=True, null=True)
    questions = models.TextField(blank=True, null=True)
    

class FieldTrip(BaseModel, BaseTimestampModel):

    class AerpawSite(models.TextChoices):
        LAKE_WHEELER = 'LAKE_WHEELER', _('Lake Wheeler')
        CENTENNIAL_CAMPUS = 'CENTENNIAL_CAMPUS', _('Centennial Campus')
        OTHER = 'OTHER', _('Other')

    experiment_form = models.ManyToManyField(ExperimentFormData)
    number_of_fixed_nodes = models.SmallIntegerField(default=0)
    number_of_portable_nodes = models.SmallIntegerField(default=0)
    LAMs = models.SmallIntegerField(default=0)
    SAMs = models.SmallIntegerField(default=0)
    rovers = models.SmallIntegerField(default=0)
    helikite = models.SmallIntegerField(default=0)
    person_hours = models.FloatField(default=0)
    list_of_operators = models.CharField(max_length=255, blank=True, null=True)
    operators = models.ManyToManyField(AerpawUser, limit_choices_to={'username__endswith':'@ncsu.edu'})
    experiment_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    fixed_nodes_used = models.ManyToManyField(AerpawResource, limit_choices_to={'resource_type__in':['AFRN']})
    radio_hardware = models.CharField(max_length=255, blank=True, null=True)
    site = models.CharField(max_length=255, choices=AerpawSite.choices, blank=True, null=True)
    comments = models.CharField(max_length=500, blank=True, null=True)
    is_canceled = models.BooleanField(default=False)

    
    
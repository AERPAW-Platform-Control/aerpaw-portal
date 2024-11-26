from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from portal.apps.mixins.models import BaseModel, BaseTimestampModel
from portal.apps.experiments.models import AerpawExperiment

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

    class ExperimentType(models.TextChoices):
        CANONICAL = 'canonical', _('Canonical')
        NON_CANONICAL = 'non_canonical', _('Non-Canonical')
        CUSTOM = 'custom', _('Custom')
    
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
    public_url = models.URLField(blank=True, null=True)
    goal = models.TextField()
    vehicle_behavior = models.TextField()
    description = models.TextField(blank=True, null=True)
    byod_hardware = models.TextField(blank=True, null=True)
    byod_software = models.TextField(blank=True, null=True)
    questions = models.TextField(blank=True, null=True)
    sponsored_project = models.CharField(max_length=255, blank=True, null=True)
    grant_number = models.CharField(max_length=255, blank=True, null=True)




    
    
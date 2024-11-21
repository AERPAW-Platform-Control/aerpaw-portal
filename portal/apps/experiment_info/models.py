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

    
    title = models.CharField(max_length=255)
    host_institution = models.CharField(max_length=255, blank=True, null=True)
    lead_experimenter = models.CharField(max_length=255, blank=True, null=True)
    lead_email = models.EmailField()
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        abstract = True


class GAExperimentFormData(ExperimentFormData):
    """  
    id - from BaseModel
    created - datetime from BaseTimestampModel
    modified - datetime from BaseTimestampModel
    experiment - forgien key
    title - charfield: experiment title
    host_institution - charfield
    sponsored_project - charfield: the project that encompasses this experiment if sponsored
    lead_experimenter - charfield
    lead_email - email
    keywords - charfield: 3 to 5 experiment descriptors
    goal - text field
    location - choicefield: lake wheeler, centennial campus, emulation, or sandbox
    urgent_date - datetime 
    public_url - urlfield: for sharing experiment data
    vehicle_behavior - text field
    uuid
    """

    class ExperimentLocation(models.TextChoices):
        LAKE_WHEELER = 'lake_wheeler', _('Lake Wheeler')
        CENTENNIAL_CAMPUS = 'centennial_campus', _('Centennial Campus')
        EMULATION = 'emulation', _('Emulation')
        SANDBOX = 'sandbox', _('Sandbox')
       
    experiment = models.ForeignKey(AerpawExperiment, on_delete=models.CASCADE, blank=True, null=True)
    urgency_date = models.DateField(blank=True, null=True)
    sponsored_project = models.CharField(max_length=255, blank=True, null=True)
    grant_number = models.CharField(max_length=255, blank=True, null=True)
    keywords = models.CharField(max_length=255, blank=True, null=True)
    location = ArrayField(models.CharField(max_length=255, choices=ExperimentLocation.choices), blank=True, default=list)
    public_url = models.URLField(blank=True, null=True)
    goal = models.TextField()
    vehicle_behavior = models.TextField()
    

class CustomExperimentFormData(ExperimentFormData):
    """  
    id - from BaseModel
    created - from BaseTimestampModel
    modified - from BaseTimestampModel
    experiment = ForiegnKey
    lead_experimenter - Charfield
    lead_email - EmailField
    host_institution - CharField
    title - CharField
    description - TextField
    byod_hardware - TextField
    byod_software - TextField
    questions - TextField
    uuid
    """
   
    description = models.TextField()
    byod_hardware = models.TextField()
    byod_software = models.TextField()
    questions = models.TextField()
    sponsored_project = models.CharField(max_length=255, blank=True, null=True)
    grant_number = models.CharField(max_length=255, blank=True, null=True)
    
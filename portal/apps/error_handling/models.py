from django.db import models
from django.utils.translation import gettext_lazy as _
from portal.apps.mixins.models import AuditModelMixin, BaseModel, BaseTimestampModel
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser
# Create your models here.

class AerpawError(BaseModel, models.Model):
    """ 
    Errors
    - id (from BaseModel)
    - user (the user that the error happened to)
    - is_resolved

    """
    user = models.ForeignKey(AerpawUser, on_delete=models.SET_NULL, null=True)
    datetime = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    traceback = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    displayed = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(AerpawUser, on_delete=models.SET_NULL, null=True, related_name='resolved_by')
    resolved_datetime = models.DateTimeField(auto_now=False, null=True, blank=True)
    resolved_description = models.TextField(blank=True, null=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)


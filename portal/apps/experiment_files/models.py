from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from portal.apps.mixins.models import AuditModelMixin, BaseModel, BaseTimestampModel
from portal.apps.operations.models import CanonicalNumber
from portal.apps.projects.models import AerpawProject
from portal.apps.resources.models import AerpawResource
from portal.apps.users.models import AerpawUser


class ExperimentFile(BaseModel, AuditModelMixin, models.Model):
    """
    Experiment file
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - file_location
    - file_name
    - file_type
    - id (from Basemodel)
    - is_deleted
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - notes
    - uuid
    """

    class LinkedFileType(models.TextChoices):
        IP_LIST = 'ip_list', _('IP List')
        OVPN = 'ovpn', _('OVPN')

    is_deleted = models.BooleanField(default=False)
    file_location = models.CharField(max_length=255, blank=False, null=False)
    file_name = models.CharField(max_length=255, blank=False, null=False)
    file_type = models.CharField(
        max_length=255,
        choices=LinkedFileType.choices,
        default=LinkedFileType.OVPN
    )
    notes = models.TextField(blank=True, null=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        ordering = ['file_name']

    def __str__(self):
        max_length = 40
        display_name = '{0} - {1}'.format(self.file_name, self.notes) if self.notes else self.file_name
        str_end = '...'
        length = len(display_name)
        if length > max_length:
            return display_name[:max_length - len(str_end)] + str_end

        return display_name

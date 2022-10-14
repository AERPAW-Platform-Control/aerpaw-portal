from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from portal.apps.mixins.models import AuditModelMixin, BaseModel
from portal.apps.profiles.models import AerpawUserProfile
from portal.apps.users.models import AerpawUser


class AerpawUserRequest(BaseModel, AuditModelMixin, models.Model):
    """
    UserRequests
    - completed_by (fk) - user_id
    - completed_date - UTC
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - id (from Basemodel) - request_id
    - is_approved - bool
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - received_by (fk) - array of user_id
    - request_date - UTC - same as "created"
    - request_note - string
    - request_type - [experiment, project, role]
    - request_type_id (fk) - int
    - requested_by (fk) - user_id
    - response_date - UTC
    - response_note - string
    - uuid
    """

    class RequestType(models.TextChoices):
        EXPERIMENT = 'experiment', _('Experiment')
        PROJECT = 'project', _('Project')
        ROLE = 'role', _('Role')

    completed_by = models.ForeignKey(
        AerpawUser,
        related_name='request_completed_by',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    completed_date = models.DateTimeField(blank=True, null=True)
    is_approved = models.BooleanField(blank=True, null=True)
    received_by = models.ManyToManyField(
        AerpawUser,
        related_name='user_request_received_by'
    )
    request_note = models.TextField(blank=True, null=True)
    request_type = models.CharField(
        max_length=255,
        choices=RequestType.choices,
        default=RequestType.ROLE
    )
    request_type_id = models.IntegerField(blank=False, null=False)
    requested_by = models.ForeignKey(
        AerpawUser,
        related_name='requested_by',
        on_delete=models.CASCADE
    )
    response_date = models.DateTimeField(blank=True, null=True)
    response_note = models.TextField(blank=True, null=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        verbose_name = 'AERPAW User Request'

    def __str__(self):
        return self.request_type

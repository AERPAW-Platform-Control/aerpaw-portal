from django.db import models

from portal.apps.mixins.models import AuditModelMixin, BaseModel
from portal.apps.users.models import AerpawUser


class AerpawUserMessage(BaseModel, AuditModelMixin, models.Model):
    """
    UserMessages
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - id (from Basemodel) - request_id
    - is_deleted - bool
    - is_read - bool
    - message_body - string
    - message_owner - int:user_id
    - message_subject - string
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - read_date - string
    - received_by (fk) - array of int:user_id
    - sent_by (fk) - int:user_id
    - uuid
    """

    is_deleted = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    message_body = models.TextField(blank=True, null=True)
    message_owner = models.ForeignKey(
        AerpawUser,
        related_name='user_message_owner',
        on_delete=models.PROTECT
    )
    message_subject = models.TextField(blank=True, null=True)
    read_date = models.DateTimeField(blank=True, null=True)
    received_by = models.ManyToManyField(
        AerpawUser,
        related_name='user_message_received_by'
    )
    sent_by = models.ForeignKey(
        AerpawUser,
        related_name='user_message_sent_by',
        on_delete=models.PROTECT
    )
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        verbose_name = 'AERPAW User Message'

    def __str__(self):
        return self.message_subject

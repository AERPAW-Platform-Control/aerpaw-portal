from datetime import datetime, timedelta, timezone

from django.db import models

from portal.apps.mixins.models import AuditModelMixin, BaseModel
from portal.apps.users.models import AerpawUser

# constants
CREDENTIAL_EXPIRY_DAYS = 365


class PublicCredentials(BaseModel, AuditModelMixin):
    """
    Public User Credentials
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - expiry_date
    - id (from Basemodel)
    - is_deleted
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - name
    - owner
    - public_credential
    - uuid
    """

    expiry_date = models.DateTimeField(default=datetime.now(timezone.utc) + timedelta(days=CREDENTIAL_EXPIRY_DAYS))
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    owner = models.ForeignKey(
        AerpawUser,
        related_name='public_credential_owner',
        on_delete=models.PROTECT
    )
    public_credential = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

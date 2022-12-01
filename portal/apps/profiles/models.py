from django.contrib.auth.models import AbstractUser
from django.db import models

from portal.apps.mixins.models import AuditModelMixin, BaseModel


class AerpawUserProfile(BaseModel, AuditModelMixin):
    """
    User Profile
    - access_token
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - employer
    - id (from Basemodel)
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - position
    - refresh_token
    - research_field
    - uuid
    """

    access_token = models.TextField(null=True, blank=True)
    employer = models.TextField(null=True, blank=True)
    position = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    research_field = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    def __str__(self):
        return self.uuid

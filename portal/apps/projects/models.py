from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from portal.apps.mixins.models import AuditModelMixin, BaseModel
from portal.apps.profiles.models import AerpawUserProfile
from portal.apps.users.models import AerpawUser


class AerpawProject(BaseModel, AuditModelMixin, models.Model):
    """
    Projects
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - description
    - id (from Basemodel)
    - is_deleted
    - is_public
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - name
    - project_creator (fk)
    - project_personnel (m2m)
    - uuid
    """
    description = models.TextField()
    is_deleted = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    project_creator = models.ForeignKey(
        AerpawUser,
        related_name='project_creator',
        on_delete=models.PROTECT
    )
    project_personnel = models.ManyToManyField(
        AerpawUser,
        related_name='project_personnel',
        through='UserProject',
        through_fields=('project', 'user')
    )
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        verbose_name = 'AERPAW Project'

    def __str__(self):
        return self.name

    def is_creator(self, user: AerpawUser) -> bool:
        return user == self.project_creator

    def is_member(self, user: AerpawUser) -> bool:
        return UserProject.objects.filter(
            user=user, project=self, project_role=UserProject.RoleType.PROJECT_MEMBER).exists()

    def is_owner(self, user: AerpawUser) -> bool:
        return UserProject.objects.filter(
            user=user, project=self, project_role=UserProject.RoleType.PROJECT_OWNER).exists()


class UserProject(BaseModel, models.Model):
    """
    User-Project relationship
    - granted_by
    - granted_date
    - id (from Basemodel)
    - project_id
    - project_role
    - user
    """

    class RoleType(models.TextChoices):
        PROJECT_MEMBER = 'project_member', _('Project Member')
        PROJECT_OWNER = 'project_owner', _('Project Owner')

    granted_by = models.ForeignKey(AerpawUser, related_name='project_granted_by', on_delete=models.CASCADE)
    granted_date = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(AerpawProject, on_delete=models.CASCADE)
    project_role = models.CharField(
        max_length=255,
        choices=RoleType.choices,
        default=RoleType.PROJECT_MEMBER
    )
    user = models.ForeignKey(AerpawUser, related_name='project_user', on_delete=models.CASCADE)
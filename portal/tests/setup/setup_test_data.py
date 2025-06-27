from portal.apps.experiments.models import AerpawExperiment
from portal.apps.operations.models import CanonicalNumber
from portal.apps.resources.models import AerpawResource
from portal.apps.users.models import AerpawUser
from portal.apps.profiles.models import AerpawUserProfile


for i in range(1,31):
    """  - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - date_joined (from AbstractUser)
    - display_name
    - email (from AbstractUser)
    - first_name (from AbstractUser)
    - groups (from AbstractUser)
    - id (from Basemodel)
    - is_active (from AbstractUser)
    - is_staff (from AbstractUser)
    - is_superuser (from AbstractUser)
    - last_login (from AbstractUser)
    - last_name (from AbstractUser)
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - openid_sub
    - password (from AbstractUser)
    - profile
    - user_permissions (from AbstractUser)
    - username (from AbstractUser)
    - uuid """
    user = AerpawUser.objects.create(
        
    )



    """ access_token
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - employer
    - id (from Basemodel)
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - position
    - refresh_token
    - research_field
    - uuid """
    profile = AerpawUserProfile.objects.create(
        
    )
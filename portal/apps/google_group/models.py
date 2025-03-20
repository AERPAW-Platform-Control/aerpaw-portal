from django.db import models
from portal.apps.mixins.models import BaseModel, BaseTimestampModel
from portal.apps.users.models import AerpawUser


class UserGoogleGroupConsent(BaseModel, BaseTimestampModel, models.Model):
    """ 
    This model is used to track if users have given consent to be added to 
    the Aerpaw Users Google Group using Google APIs in the portal

    Fields:
    - id  from BaseModel
    - created  from BaseTimestampModel
    - modified  from BaseTimestampModel
    - user
    - consent

    """
    user = models.ForeignKey(AerpawUser, on_delete=models.CASCADE)
    consent_given = models.BooleanField()


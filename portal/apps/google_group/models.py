from django.db import models
from portal.apps.mixins.models import BaseModel, BaseTimestampModel
from portal.apps.users.models import AerpawUser


class GoogleGroupMembership(BaseModel, BaseTimestampModel, models.Model):
    """ 
    This model is used to track if users have given consent to be added to 
    the Aerpaw Users Google Group using Google APIs in the portal

    Fields:
    - id  from BaseModel
    - created  from BaseTimestampModel
    - modified  from BaseTimestampModel
    - user
    - consent_asked - has the user been asked if they are willing to join the google group
    - consent_given - has the user given consent to auto join the google group
    - member - Is the user a mamber of the google group

    """
    user = models.ForeignKey(AerpawUser, on_delete=models.CASCADE)
    consent_asked = models.BooleanField(default=False)
    consent_given = models.BooleanField(default=False)
    member = models.BooleanField(default=False)

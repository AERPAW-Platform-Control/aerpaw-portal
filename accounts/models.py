# accounts/models.py
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum

class AerpawUserRoleChoice(Enum):   # A subclass of Enum
    ADMIN = 'Admin'
    PI = 'PI'
    LEADEXPERIMENTER = 'Lead Experimenter'
    EXPERIMENTER = 'Experimenter'
    OBSERVERS = 'Observers'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

# Extends basic User model: https://docs.djangoproject.com/en/3.1/ref/contrib/auth/
class AerpawUser(AbstractUser):
    # universal unique identifier for user within infrastructure
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)

    # oidc scope openid
    oidc_claim_sub = models.CharField(max_length=255)
    oidc_claim_iss = models.CharField(max_length=255)
    oidc_claim_aud = models.CharField(max_length=255)
    oidc_claim_token_id = models.CharField(max_length=255)

    # oidc scope email
    oidc_claim_email = models.CharField(max_length=255)

    # oidc scope profile
    oidc_claim_given_name = models.CharField(max_length=255)
    oidc_claim_family_name = models.CharField(max_length=255)
    oidc_claim_name = models.CharField(max_length=255)

    # oidc scope org.cilogon.userinfo
    oidc_claim_idp = models.CharField(max_length=255)
    oidc_claim_idp_name = models.CharField(max_length=255)
    oidc_claim_eppn = models.CharField(max_length=255)
    oidc_claim_eptid = models.CharField(max_length=255)
    oidc_claim_affiliation = models.CharField(max_length=255)
    oidc_claim_ou = models.CharField(max_length=255)
    oidc_claim_oidc = models.CharField(max_length=255)
    oidc_claim_cert_subject_dn = models.CharField(max_length=255)

    # oidc other values
    oidc_claim_acr = models.CharField(max_length=255)
    oidc_claim_entitlement = models.CharField(max_length=255)

    # ssh public key
    publickey = models.TextField(null=True)

    def __str__(self):
        return self.oidc_claim_name + ' (' + self.username + ')'

def is_PI(user):
    print(user)
    print(user.groups.all())
    return user.groups.filter(name='PI').exists()


def is_project_member(user,project_group):
    print(user)
    print(user.groups.all())
    return user.groups.filter(name=project_group).exists()


class AerpawUserSignup(models.Model):
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(AerpawUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    description = models.TextField()
    userRole = models.CharField(
      max_length=64,
      choices=AerpawUserRoleChoice.choices(),
    )
    publickey = models.TextField(null=True)

    def __str__(self):
        return self.user.oidc_claim_email


class AerpawUserCredential(models.Model):
    publickey = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.publickey


def create_new_signup(request, form):
    """

    :param request:
    :param form:
    :return:
    """

    signup = AerpawUserSignup()
    signup.uuid = uuid.uuid4()
    signup.user = request.user
    signup.name = form.data.getlist('name')[0]
    signup.title = form.data.getlist('title')[0]
    signup.organization = form.data.getlist('organization')[0]
    try:
        signup.description = form.data.getlist('description')[0]
    except ValueError as e:
        print(e)
        signup.description = None

    signup.userRole = form.data.getlist('userRole')[0]
    signup.publickey = form.data.getlist('publickey')[0]
    request.user.publickey = form.data.getlist('publickey')[0]
    request.user.save()
    signup.save()

    return str(signup.uuid)


def update_credential(request, form):
    """

    :param request:
    :param form:
    :return:
    """
    request.user.publickey = form.data.getlist('publickey')[0]
    request.user.save()
    return str(request.user.publickey)

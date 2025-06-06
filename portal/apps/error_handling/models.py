from django.db import models
from django.utils.translation import gettext_lazy as _
from portal.apps.mixins.models import AuditModelMixin, BaseModel, BaseTimestampModel
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser
# Create your models here.

class AerpawError(BaseModel, models.Model):
    """ 
    Errors
    - id (from BaseModel)
    - user (the user that the error happened to)
    - is_resolved

    """
    user = models.ForeignKey(AerpawUser, on_delete=models.SET_NULL, null=True)
    datetime = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    traceback = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    displayed = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(AerpawUser, on_delete=models.SET_NULL, null=True, related_name='resolved_by')
    resolved_datetime = models.DateTimeField(auto_now=False, null=True, blank=True)
    resolved_description = models.TextField(blank=True, null=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

class AerpawThread(BaseModel, models.Model):
    """ 
    AerpawThread
    - id (from BaseModal)
    - user (ForiegnKey to AerpawUser)
    - thread_start 
    - thread_end
    - exit_code
    - response
    - is_error
    - displayed
    - error (ForgienKey to Error)
    """
    class ThreadActions(models.TextChoices):
        SAVE_DEVELOPMENT = 'save_development', _('Save Development')
        SAVE_SANDBOX = 'save_sandbox', _('Save Sandbox')
        SAVE_EMULATION = 'save_emulation', _('Save Emulation')
        SAVE_TESTBED = 'save_testbed', _('Save Testbed')
        INITIATE_DEV = 'initiate_dev', _('Initiate Development')
        INITIATE_SB = 'initiate_sb', _('Initiate Sandbox')
        INITIATE_EM = 'initiate_em', _('Initiate Emulation')
        INITIATE_TB = 'initiate_tb', _('Initiate Testbed')
        RETIRE = 'retire', _('Retire Experiment')


    user = models.ForeignKey(AerpawUser, on_delete=models.SET_NULL, null=True)
    experiment = models.ForeignKey(AerpawExperiment, on_delete=models.CASCADE, null=True)
    action = models.CharField(
        max_length=255, 
        choices=ThreadActions.choices,
        default=None,
        blank=True,
        null=True
        )
    command = models.CharField(max_length=250, blank=True, null=True)
    thread_created = models.DateTimeField(auto_now_add=True)
    is_threaded = models.BooleanField(default=False)
    thread_end = models.DateTimeField(auto_now=False, blank=True, null=True)
    exit_code = models.SmallIntegerField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    is_error = models.BooleanField(blank=True, null=True)
    displayed = models.BooleanField(blank=True, null=True, default=False)
    error = models.ManyToManyField('AerpawError', blank=True)
    message = models.TextField(blank=True, null=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    def save(self, *args, **kwargs):
        message = ''
        if self.is_error == True:
            error_numbers = [str(error.id) for error in self.error.all()]
            message = f'Error# {self.id}:<p class="text-danger">An error has occured and {self.get_action_display()} could not be completed! <br>If this error persists, please <a class="btn btn-sm btn-outline-danger" href="mailto:cjr47@cornell.edu?subject=Error#%20{self.id}%20in%20{self.get_action_display()}">click here to email the Aerpaw Ops Team <i class="fa fa-paper-plane"></i></a></p><hr class="w-50 text-danger">'
        elif self.is_error != True and self.thread_end != None:
            message = f'{self.get_action_display()} is successful!'
            self.is_error = False
        self.message = message
        super(AerpawThread, self).save(*args, **kwargs)
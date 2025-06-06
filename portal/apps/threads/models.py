from django.db import models
from django.utils.translation import gettext_lazy as _
from portal.apps.mixins.models import AuditModelMixin, BaseModel
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser

# Create your models here.

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

    def save(self, request, *args, **kwargs):
        message = ''
        if self.is_error == True:
            error_numbers = [str(error.id) for error in self.error.all()]
            message = f'Error# {self.id}:<p class="text-danger">An error has occured and {self.get_action_display()} could not be completed! <br>If this error persists, please <a class="btn btn-sm btn-outline-danger" href="mailto:cjr47@cornell.edu?subject=Error#%20{self.id}%20in%20{self.get_action_display()}">click here to email the Aerpaw Ops Team <i class="fa fa-paper-plane"></i></a></p><hr class="w-50 text-danger">'
        elif self.is_error != True and self.thread_end != None:
            message = f'{self.get_action_display()} is successful!'
            self.is_error = False
        self.message = message
        super(AerpawThread, self).save(*args, **kwargs)

    


class ThreadQue(AuditModelMixin, models.Model):

    class ThreadTargets(models.TextChoices):
        WAIT_DEVELOPMENT_DEPLOY = 'wait_development_deploy', _('Wait Development Deploy')
        SAVING_DEVELOPMENT = 'saving_development', _('Saving Development')
        WAIT_SANDBOX_DEPLOY = 'wait_sandbox_deploy', _('Wait Sandbox Deploy')
        SAVING_SANDBOX = 'saving_sandbox', _('Saving Sandbox')
        WAIT_TESTBED_SCHEDULE = 'wait_testbed_schedule', _('Wait Testbed Schedule')
        RETIRED = 'retired', _('Retired')
        

    threads = models.ManyToManyField('AerpawThread')
    is_threading = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    target = models.CharField(max_length=255)

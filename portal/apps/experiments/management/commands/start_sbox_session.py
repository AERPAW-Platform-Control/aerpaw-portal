import threading
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from portal.apps.error_handling.error_dashboard import new_error, start_aerpaw_thread, end_aerpaw_thread, add_error_to_thread
from portal.apps.error_handling.models import AerpawThread
from portal.apps.experiments.api.experiment_utils import wait_sandbox_deploy_to_active_sandbox
from portal.apps.experiments.models import ScheduledSession
from portal.server.ops_ssh_utils import AerpawSsh
from portal.server.settings import MOCK_OPS


class Command(BaseCommand):
    help = 'This function will run at 6:30am every day.  It starts a new sandbox session if a sbox session is schedued to start on this day.'

    def handle(self, *args, **kwargs):
        try:
            # First: check for active sbox sessions
            today = timezone.now()
            session = ScheduledSession.objects.filter(scheduled_start=today).first()
            if session:
                # start session
                experiment = session.experiment
                wait_sandbox_deploy_to_active_sandbox(None, experiment)

        except:
            try:
                raise CommandError('Sandbox Initalization failed.')
            except CommandError as exc:
                new_error(exc, experiment.created_by)
        

        
        

    

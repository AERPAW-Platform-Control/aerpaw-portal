from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.experiments.models import ScheduledSession


class Command(BaseCommand):
    help = 'This function will run at 5:35am every day.  It ends the current sandbox session if its end date is on this day.'

    def handle(self, *args, **kwargs):
        today = timezone.now()
        session = ScheduledSession.objects.filter(scheduled_end=today).first()
        experiment = session.experiment
        try:
            if session:
                # end current session
                self.end_sbox_session

        except:
            try:
                raise CommandError('Sandbox Initalization failed.')
            except CommandError as exc:
                new_error(exc, experiment.created_by)

    def check_active_session_ends_today(self, session: ScheduledSession):
        print('this function will check the currently active sandbox session for its end date and return true if it is today and false if NOT today')

    def end_sbox_session(self, session: ScheduledSession):
        print('this function will end a current sandbox session')
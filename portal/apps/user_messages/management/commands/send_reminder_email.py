from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta

from portal.apps.experiments.models import AerpawExperiment, ScheduledSession, OnDemandSession


def send_sandbox_start_reminder():
    print(' ')
    today = timezone.now()
    sandbox_sessions = ScheduledSession.objects.filter(session_type=OnDemandSession.SessionType.SANDBOX, is_active=True, scheduled_start__gt=today)
    if sandbox_sessions.exists():
        for session in sandbox_sessions:
            time_until_start = session.scheduled_start - today
            if  time_until_start.days <= 1:
                print(f'A reminder email for session {session} will be sent here')
    else:
        print('No upcoming Sandbox Sessions')

def send_sandbox_ending_reminder():
    print()
    today = timezone.now()
    session = ScheduledSession.objects.filter(session_type=OnDemandSession.SessionType.SANDBOX, is_active=True)


class Command(BaseCommand):
    help = 'Performs daily checks on Scheduled Sessions to send an email to experimentors the day before their sandbox session starts and an hour before it ends.'

    def handle(self, *args, **kwargs):
        print('The ability tro auto send reminder emails will be ready soon.')
        send_sandbox_start_reminder()
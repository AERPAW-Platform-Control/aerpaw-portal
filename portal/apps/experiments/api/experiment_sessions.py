from datetime import datetime, timezone, timedelta
from django.utils import timezone as tz
from uuid import uuid4

from portal.apps.experiments.models import AerpawExperiment, OnDemandSession, ScheduledSession
from portal.apps.users.models import AerpawUser


def create_experiment_session(session_type: str, experiment: AerpawExperiment, user: AerpawUser) -> OnDemandSession:
    """
    Experiment Session
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - ended_by
    - ended_date_time
    - experiment
    - id (from Basemodel)
    - is_active
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - session_type
    - start_date_time
    - started_by
    - uuid
    """
    session = OnDemandSession()
    session.created_by = user.username
    session.experiment = experiment
    session.is_active = True
    session.modified_by = user.username
    session.session_type = session_type
    session.uuid = uuid4()
    session.save()

    return session


def start_experiment_session(session: OnDemandSession, user: AerpawUser) -> bool:
    try:
        session.is_active = True
        session.modified_by = user.username
        session.start_date_time = datetime.now(timezone.utc)
        session.started_by = user
        session.save()
        return True
    except Exception as exc:
        print(exc)
    return False


def stop_experiment_session(session: OnDemandSession, user: AerpawUser) -> bool:
    try:
        session.end_date_time = datetime.now(timezone.utc)
        session.ended_by = user
        session.is_active = False
        session.modified_by = user.username
        session.save()
        return True
    except Exception as exc:
        print(exc)
    return False


def cancel_experiment_session(session: OnDemandSession, user: AerpawUser) -> bool:
    try:
        session.end_date_time = None
        session.is_active = False
        session.modified_by = user.username
        session.start_date_time = None
        session.save()
        return True
    except Exception as exc:
        print(exc)
    return False


def create_experiment_scheduled_session(session_type: str, experiment: AerpawExperiment, user: AerpawUser, scheduled_active_date:datetime =None) -> ScheduledSession:
    """
    Ops Session - created by Aerpaw Ops team to manually manage sessions 
    - description (an explanation to be emailed to experimenters describing success status)
    - scheduled_by
    - scheduled_created_on (date the scheduled date_time was created)
    - scheduled_date_time (date the session will occur)
    - canceled_by
    - canceled
    - session_state (the place the session is currently in the session workflow)
    - is_success

    Inherits from Experiment Session
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - ended_by
    - ended_date_time
    - experiment
    - id (from Basemodel)
    - is_active
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - session_type
    - start_date_time
    - started_by
    - uuid

    Individual Sandbox Sessions run from 10:00 am to 5:00 am 
    """
    match session_type:
        case 'development':
            scheduled_start = None
            scheduled_end = None
            session_state = ScheduledSession.SessionStateChoices.SCHEDULED
        case 'sandbox':
            scheduled_start = datetime.strptime(f'{scheduled_active_date[0]}T10:00', "%Y-%m-%dT%H:%M")
            scheduled_end = None
            if len(scheduled_active_date) >1:
                scheduled_end = datetime.strptime(f'{scheduled_active_date[len(scheduled_active_date)-1]}T05:00', "%Y-%m-%dT%H:%M") +timedelta(days=1)
            else:
                scheduled_end = scheduled_start + timedelta(hours=19)
            session_state = ScheduledSession.SessionStateChoices.SCHEDULED
        case 'emulation':
            scheduled_start = None
            scheduled_end = None
            session_state = ScheduledSession.SessionStateChoices.SCHEDULED
        case 'testbed':
            scheduled_start = None
            scheduled_end = None
            session_state = ScheduledSession.SessionStateChoices.WAIT_SCHEDULE
        case _:
            scheduled_start = None
            scheduled_end = None
            session_state = ScheduledSession.SessionStateChoices.WAIT_SCHEDULE
    session = ScheduledSession()
    session.created_by = user.username
    session.experiment = experiment
    session.is_active = True
    session.modified_by = user.username
    session.session_state = session_state
    session.session_type = session_type
    session.scheduled_start = scheduled_start
    session.scheduled_end = scheduled_end
    session.uuid = uuid4()
    session.save()

    return session


def schedule_experiment_scheduled_session(request, session: ScheduledSession, user: AerpawUser) -> bool:
    try:
        # need to save scheduled_by 
        scheduled_date_time = datetime.strptime(request.data["session_date"]+ 'T' + request.data["session_time"], '%Y-%m-%dT%H:%M')
        scheduled_date_time = tz.make_aware(scheduled_date_time)
        session.scheduled_start = scheduled_date_time
        session.scheduled_created_on = tz.now()
        session.scheduled_by = user
        session.session_state = ScheduledSession.SessionStateChoices.SCHEDULED
        session.save()
        return True
    except Exception as exc:
        print(exc)
    return False


def start_scheduled_session(session: ScheduledSession, user: AerpawUser) -> bool:
    try:
        session.is_active = True
        session.modified_by = user.username
        session.start_date_time = datetime.now(timezone.utc)
        session.started_by = user
        session.session_state = ScheduledSession.SessionStateChoices.STARTED
        session.save()
        return True
    except Exception as exc:
        print(exc)
    return False


def end_scheduled_session(request, session: ScheduledSession, user: AerpawUser) -> bool:
    try:
        session.is_active = False
        session.modified_by = user.username
        session.end_date_time = datetime.now(timezone.utc)
        session.ended_by = user
        session.session_state = ScheduledSession.SessionStateChoices.COMPLETED
        session.description = request.data['session_description']
        session.is_success = request.data['is_success'] if request.data['is_success'] else False
        session.save()
        return True
    except Exception as exc:
        print('SESSIONS exc',exc)
        return False


def cancel_scheduled_session(request, session: ScheduledSession, user: AerpawUser) -> bool:
    try:
        session.is_active = False
        session.modified_by = user.username
        session.end_date_time = datetime.now(timezone.utc)
        session.ended_by = user
        session.session_state = ScheduledSession.SessionStateChoices.CANCELED
        session.description = request.data['session_description']
        session.is_success = request.data['is_success'] if request.data['is_success'] else False
        session.save()
        return True
    except Exception as exc:
        print('SESSIONS exc',exc)
        return False



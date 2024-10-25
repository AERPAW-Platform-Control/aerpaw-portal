from datetime import datetime, timezone
from django.utils import timezone as tz
from uuid import uuid4

from portal.apps.experiments.models import AerpawExperiment, ExperimentSession, OpsSession
from portal.apps.users.models import AerpawUser


def create_experiment_session(session_type: str, experiment: AerpawExperiment, user: AerpawUser) -> ExperimentSession:
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
    session = ExperimentSession()
    session.created_by = user.username
    session.experiment = experiment
    session.is_active = True
    session.modified_by = user.username
    session.session_type = session_type
    session.uuid = uuid4()
    session.save()

    return session


def start_experiment_session(session: ExperimentSession, user: AerpawUser) -> bool:
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


def stop_experiment_session(session: ExperimentSession, user: AerpawUser) -> bool:
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


def cancel_experiment_session(session: ExperimentSession, user: AerpawUser) -> bool:
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


def create_experiment_ops_session(session_type: str, experiment: AerpawExperiment, user: AerpawUser) -> OpsSession:
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
    """
    session = OpsSession()
    session.created_by = user.username
    session.experiment = experiment
    session.is_active = True
    session.modified_by = user.username
    session.session_state = OpsSession.SessionStateChoices.WAIT_SCHEDULE
    session.session_type = session_type
    session.uuid = uuid4()
    session.save()

    return session


def schedule_experiment_ops_session(request, session: OpsSession, user: AerpawUser) -> bool:
    try:
        # need to save scheduled_by 
        scheduled_date_time = datetime.strptime(request.data["session_date"]+ 'T' + request.data["session_time"], '%Y-%m-%dT%H:%M')
        scheduled_date_time = tz.make_aware(scheduled_date_time)
        session.scheduled_active_date = scheduled_date_time
        session.scheduled_created_on = tz.now()
        session.scheduled_by = user
        session.session_state = OpsSession.SessionStateChoices.SCHEDULED
        session.save()
        return True
    except Exception as exc:
        print(exc)
    return False


def start_ops_session(session: OpsSession, user: AerpawUser) -> bool:
    try:
        session.is_active = True
        session.modified_by = user.username
        session.start_date_time = datetime.now(timezone.utc)
        session.started_by = user
        session.session_state = OpsSession.SessionStateChoices.STARTED
        session.save()
        return True
    except Exception as exc:
        print(exc)
    return False


def end_ops_session(request, session: OpsSession, user: AerpawUser) -> bool:
    print('SESSIONS end_ops_session')
    print('SESSIONS request.data', request.data)
    print('SESSIONS ', session)

    try:
        session.is_active = False
        session.modified_by = user.username
        session.end_date_time = datetime.now(timezone.utc)
        session.ended_by = user
        session.session_state = OpsSession.SessionStateChoices.COMPLETED
        session.description = request.data['session_description']
        session.is_success = request.data['is_success'] if request.data['is_success'] else False
        session.save()
        return True
    except Exception as exc:
        print('SESSIONS exc',exc)
        return False

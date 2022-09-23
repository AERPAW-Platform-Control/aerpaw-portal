from datetime import datetime, timezone
from uuid import uuid4

from portal.apps.experiments.models import AerpawExperiment, ExperimentSession
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

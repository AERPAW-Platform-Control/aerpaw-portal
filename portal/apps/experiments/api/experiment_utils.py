from rest_framework.exceptions import NotFound

from portal.apps.experiments.api.experiment_sessions import cancel_experiment_session, create_experiment_session, \
    start_experiment_session, stop_experiment_session
from portal.apps.experiments.models import AerpawExperiment, ExperimentSession


def active_development_to_saved(request, experiment: AerpawExperiment):
    """
    ACTIVE_DEVELOPMENT --> SAVED
    - save development session
    - Flags 000 (e.g. experimenter logged out of all VMs for one hour)

    Session: update DEVELOPMENT --> end_date_time, ended_by, is_active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # get active session and stop
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    stop_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '000'
    experiment.save()


def active_emulation_to_saved(request, experiment: AerpawExperiment):
    """
    ACTIVE_EMULATION --> SAVED
    - emulation complete
    - Flags 100 or 101

    Session: update EMULATION --> end_date_time, ended_by, is_active=False

    Permissions:
    - operator
    """
    # get active session and stop
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    stop_experiment_session(session=session, user=request.user)
    # update experiment state
    try:
        emulation_passed = request.data.get('emulation_passed', False)
    except Exception as exc:
        print(exc)
        emulation_passed = False
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    if emulation_passed:
        experiment.experiment_flags = '101'
    else:
        experiment.experiment_flags = '100'
    experiment.save()


def active_sandbox_to_saved(request, experiment: AerpawExperiment):
    """
    ACTIVE_SANDBOX --> SAVED
    - save sandbox session
    - Flags 000 (e.g. end of scheduled sandbox session)

    Session: update SANDBOX --> end_date_time, ended_by, is_active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # get active session and stop
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    stop_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '000'
    experiment.save()


def active_testbed_to_saved(request, experiment: AerpawExperiment):
    """
    ACTIVE_TESTBED --> SAVED
    - execution complete
    - Flags 010

    Session: update TESTBED --> end_date_time, ended_by, is_active=False

    Permissions:
    - operator
    """
    # get active session and stop
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    stop_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '010'
    experiment.save()


def saved_to_wait_development_deploy(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_DEVELOPMENT_DEPLOY
    - start development session

    Session: create DEVELOPMENT --> created, created_by

    Permissions:
    - experimenter
    """
    # create new DEVELOPMENT session
    create_experiment_session(
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        experiment=experiment,
        user=request.user
    )
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY
    experiment.save()


def saved_to_wait_sandbox_deploy(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_SANDBOX_DEPLOY
    - schedule sandbox session

    Session: create SANDBOX --> created, created_by

    Permissions:
    - experimenter
    """
    # create new SANDBOX session
    create_experiment_session(
        session_type=ExperimentSession.SessionType.SANDBOX,
        experiment=experiment,
        user=request.user
    )
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY
    experiment.save()


def saved_to_wait_emulation_schedule(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_EMULATION_SCHEDULE
    - reqeust emulation session

    Session: create EMULATION --> created, created_by

    Permissions:
    - experimenter
    """
    # create new EMULATION session
    create_experiment_session(
        session_type=ExperimentSession.SessionType.EMULATION,
        experiment=experiment,
        user=request.user
    )
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE
    experiment.save()


def saved_to_wait_testbed_schedule(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_TESTBED_SCHEDULE
    - request testbed session (allowed if (E&&P)|T

    Session: create TESTBED --> created, created_by

    Permissions:
    - experimenter
    """
    # create new TESTBED session
    create_experiment_session(
        session_type=ExperimentSession.SessionType.TESTBED,
        experiment=experiment,
        user=request.user
    )
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE
    experiment.save()


def wait_development_deploy_to_active_development(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> ACTIVE_DEVELOPMENT
    - deployment on development VMs complete

    Session: update DEVELOPMENT --> start_date_time, started_by

    Permissions:
    - operator
    """
    # get active session and start
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    start_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_DEVELOPMENT
    experiment.experiment_flags = '000'
    experiment.save()


def wait_development_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> SAVED
    - failure to deploy

    Session: update DEVELOPMENT --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_emulation_deploy_to_active_emulation(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_DEPLOY --> ACTIVE_EMULATION
    - scheduled deployment of emulation complete

    Session: update EMULATION --> start_date_time, started_by

    Permissions:
    - operator
    """
    # get active session and start
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    start_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_EMULATION
    experiment.save()


def wait_emulation_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> SAVED
    - failure to deploy

    Session: update EMULATION --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_emulation_schedule_to_wait_emulation_deploy(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_SCHEDULE --> WAIT_EMULATION_DEPLOY
    - schedule

    Session: update EMULATION --> active=True

    Permissions:
    - operator
    """
    # no change to session
    # get active session and update
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_DEPLOY
    experiment.save()


def wait_emulation_schedule_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_SCHEDULE --> SAVED
    - cancel pending emulation session

    Session: update EMULATION --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)
    # update experiment state
    # get active session and update
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_sandbox_deploy_to_active_sandbox(request, experiment: AerpawExperiment):
    """
    WAIT_SANDBOX_DEPLOY --> ACTIVE_SANDBOX
    - scheduled deployment on sandbox complete

    Session: update SANDBOX --> start_date_time, started_by

    Permissions:
    - operator
    """
    # get active session and start
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    start_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_SANDBOX
    experiment.experiment_flags = '000'
    experiment.save()


def wait_sandbox_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_SANDBOX_DEPLOY --> SAVED
    - cancel pending sandbox session

    Session: update SANDBOX --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_testbed_deploy_to_active_testbed(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_DEPLOY --> ACTIVE_TESTBED
    - scheduled deployment of testbed complete

    Session: update TESTBED --> start_date_time, started_by

    Permissions:
    - operator
    """
    # get active session and start
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    start_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_TESTBED
    experiment.save()


def wait_testbed_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_DEPLOY --> SAVED
    - cancel

    Session: update TESTBED --> active=False

    Permissions:
    - operator
    """
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_testbed_schedule_to_wait_testbed_deploy(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_SCHEDULE --> WAIT_TESTBED_DEPLOY
    - schedule

    Session: update TESTBED --> active=True

    Permissions:
    - operator
    """
    # no change to session
    # get active session and update
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_DEPLOY
    experiment.save()


def wait_testbed_schedule_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_SCHEDULE --> SAVED
    - cancel pending testbed session

    Session: update TESTBED --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # get active session and cancel
    session = ExperimentSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ExperimentSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        raise NotFound(
            detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
    cancel_experiment_session(session=session, user=request.user)
    # update experiment state
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def same_to_same(request, experiment: AerpawExperiment):
    """
    Placeholder for same state update options

    Permissions:
    - experimenter OR
    - operator
    """
    # TODO: placeholder for same state update options
    pass

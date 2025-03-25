"""
Define the following for each transition between states
- PREFLIGHT CHECK: Preflight validation for requested state change / logic / data collection
- ACTION ITEMS: Transition action items (e.g. start/stop Session)
- UPDATE STATE: Update experiment state
- PORTAL CF: portal control framework decision points
"""

import os
import threading
import time
import queue
from datetime import datetime, timezone, timedelta
from django.utils import timezone as tz
from rest_framework.exceptions import NotFound, ValidationError

from portal.apps.credentials.models import PublicCredentials
from portal.apps.error_handling.error_dashboard import new_error, start_aerpaw_thread, end_aerpaw_thread, add_error_to_thread
from portal.apps.error_handling.models import AerpawThread
from portal.apps.experiments.api.experiment_sessions import cancel_experiment_session, create_experiment_session, \
    start_experiment_session, stop_experiment_session, create_experiment_scheduled_session, schedule_experiment_scheduled_session, \
        start_scheduled_session, end_scheduled_session, cancel_scheduled_session
from portal.apps.experiments.models import AerpawExperiment, OnDemandSession, ScheduledSession
from portal.apps.user_messages.user_messages import generate_user_messages_for_development, generate_user_messages_for_sandbox,\
    generate_user_messages_for_emulation, generate_user_messages_for_testbed
from portal.server.ops_ssh_utils import AerpawSsh
from portal.server.settings import MOCK_OPS

aerpaw_ops_host = os.getenv('AERPAW_OPS_HOST')
aerpaw_ops_port = os.getenv('AERPAW_OPS_PORT')
aerpaw_ops_user = os.getenv('AERPAW_OPS_USER')
aerpaw_ops_key_file = os.getenv('AERPAW_OPS_KEY_FILE')
print(f'aerpaw_ops_host: {aerpaw_ops_host}')
print(f'aerpaw_ops_port: {aerpaw_ops_port}')
print(f'aerpaw_ops_user: {aerpaw_ops_user}')
print(f'aerpaw_ops_key_file: {aerpaw_ops_key_file}')
_TMP_FILE_PATH = '/tmp/aerpaw_files'


def active_development_to_saving_development(request, experiment: AerpawExperiment):
    """
    ACTIVE_DEVELOPMENT --> SAVING_DEVELOPMENT
    - save development session

    @param: exit_development

    Session: update DEVELOPMENT --> no change

    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session
    session = OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)

    # UPDATE STATE: save_development
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVING_DEVELOPMENT
    experiment.save()
    # check exit_development flag
    try:
        exit_development = request.data.get('exit_development', False)
    except Exception as exc:
        print(exc)
        new_error(exc, request.user)
        exit_development = False

    # MESSAGE / EMAIL: saving development
    generate_user_messages_for_development(request=request, experiment=experiment)

    # PORTAL CF: saving_development
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # aerpaw ops: ap-cf-saveexit-ve-exp.py
    
    if MOCK_OPS:
        # DEVELOPMENT - always pass
        mock = True
        if exit_development:
            command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-saveexit-ve-exp_cfdev.py {0} save-and-exit".format(
                experiment.id)
        else:
            command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-saveexit-ve-exp_cfdev.py {0} save".format(
                experiment.id)
    else:
        # Tutorial Server
        mock = False
        if exit_development:
            command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-saveexit-ve-exp_tut.py {0} save-and-exit".format(
                experiment.id)
        else:
            command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-saveexit-ve-exp_tut.py {0} save".format(
                experiment.id)
    try:
        aerpaw_thread = start_aerpaw_thread(request.user, experiment, AerpawThread.ThreadActions.SAVE_DEVELOPMENT)
        ssh_thread = threading.Thread(target=saving_development,
                                    args=(request, experiment, command, exit_development, mock, aerpaw_thread))
        ssh_thread.start()
        
    except Exception as exc:
        new_error(exc, request.user)


def active_sandbox_to_saving_sandbox(request, experiment: AerpawExperiment):
    """
    ACTIVE_SANDBOX --> SAVING_SANDBOX
    - save sandbox session

    @param: exit_sandbox

    Session: update SANDBOX --> no change

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session
    is_ops_session = False if 'ops_session' not in request.data else request.data.get('ops_session')
    if is_ops_session == True:
        scheduled_session = ScheduledSession.objects.filter(
                experiment=experiment, 
                session_type=ScheduledSession.SessionType.SANDBOX, 
                is_active=True
            ).first()
        if not scheduled_session:
            try:
                raise NotFound(
                    detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                new_error(exc, request.user)
        
    else:
        session = OnDemandSession.objects.filter(
            experiment_id=experiment.id,
            session_type=OnDemandSession.SessionType.SANDBOX,
            is_active=True
        ).first()
        if not session:
            try:
                raise NotFound(
                    detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                new_error(exc, request.user)

    # UPDATE STATE: save_sandbox
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVING_SANDBOX
    experiment.save()

    # check exit_sandbox flag
    try:
        exit_sandbox = request.data.get('exit_sandbox', False)
    except Exception as exc:
        print(exc)
        new_error(exc, request.user)
        exit_sandbox = False

    # PORTAL CF: save_sandbox
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # TODO: aerpaw ops: <SCRIPT> - placeholder for anticipated call
    # command = "sudo python3 /home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
    #     experiment.id)
    # if MOCK_OPS:
    #     # DEVELOPMENT - always pass
    #     mock = True
    # else:
    #     # PRODUCTION
    #     mock = False
    # ssh_thread = threading.Thread(target=wait_development_deploy, args=(request, experiment, command, mock))
    # ssh_thread.start()

    generate_user_messages_for_sandbox(request, experiment=experiment)


def saving_development_to_saved(request, experiment: AerpawExperiment):
    """
    SAVING_DEVELOPMENT --> SAVED
    - save development session
    - Flags 000 (e.g. experimenter logged out of all VMs for one hour)

    Session: update DEVELOPMENT --> end_date_time, ended_by, is_active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and stop
    session = OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()

    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)

    stop_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '000'
    experiment.save()

    # MESSAGE / EMAIL: saved development session and exit
    generate_user_messages_for_development(request=request, experiment=experiment)

    # PORTAL CF:


def saving_development_to_active_development(request, experiment: AerpawExperiment):
    """
    SAVING_DEVELOPMENT --> ACTIVE_DEVELOPMENT
    - resume development session

    Session: resume DEVELOPMENT --> no change

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session
    session = OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)

    # UPDATE STATE: wait_development_deploy
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_DEVELOPMENT
    experiment.save()

    # MESSAGE / EMAIL: resume active development
    generate_user_messages_for_development(request=request, experiment=experiment)

    # PORTAL CF: wait_development_deploy
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # TODO: aerpaw ops: <SCRIPT> - placeholder for anticipated call
    # command = "sudo python3 /home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
    #     experiment.id)
    # if MOCK_OPS:
    #     # DEVELOPMENT - always pass
    #     mock = True
    # else:
    #     # PRODUCTION
    #     mock = False
    # ssh_thread = threading.Thread(target=wait_development_deploy, args=(request, experiment, command, mock))
    # ssh_thread.start()


def saving_sandbox_to_saved(request, experiment: AerpawExperiment):
    """
    SAVING_SANDBOX --> SAVED
    - save sandbox session
    - Flags 000 (e.g. end of scheduled sandbox session)

    Session: update SANDBOX --> end_date_time, ended_by, is_active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and stop
    session = OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)

    stop_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '000'
    experiment.save()

    # PORTAL CF:


    generate_user_messages_for_sandbox(request, experiment=experiment)


def saving_sandbox_to_active_sandbox(request, experiment: AerpawExperiment):
    """
    SAVING_SANDBOX --> ACTIVE_SANDBOX
    - resume sandbox session

    Session: resume SANDBOX --> created, created_by

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session
    session = OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_SANDBOX
    experiment.experiment_flags = '000'
    experiment.save()

    # PORTAL CF: wait_sandbox_deploy
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # TODO: aerpaw ops: <SCRIPT> - placeholder for anticipated call
    # command = "sudo python3 /home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
    #     experiment.id)
    # if MOCK_OPS:
    #     # DEVELOPMENT - always pass
    #     mock = True
    # else:
    #     # PRODUCTION
    #     mock = False
    # ssh_thread = threading.Thread(target=wait_development_deploy, args=(request, experiment, command, mock))
    # ssh_thread.start()

    generate_user_messages_for_sandbox(request, experiment=experiment)


def active_emulation_to_saved(request, experiment: AerpawExperiment):
    print('UTILS active_emulation_to_saved')
    """
    ACTIVE_EMULATION --> SAVED
    - emulation complete
    - Flags 100 or 101

    @param: emulation_passed

    Session: update EMULATION --> end_date_time, ended_by, is_active=False

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    if request.data['ops_session'] == True:
        print('UTILS ops session')
        ops_session = ScheduledSession.objects.filter(experiment=experiment, is_active=True).first()
        if not ops_session:
            try:
                raise NotFound(
                    detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                new_error(exc, request.user)

        end_scheduled_session(request=request, session=ops_session, user=request.user)

        if request.data.get('is_success') == True:
            request.data.update({'emulation_passed': True})

    else:
        print('UTILS not ops')
        # get active session and stop
        session = OnDemandSession.objects.filter(
            experiment_id=experiment.id,
            session_type=OnDemandSession.SessionType.EMULATION,
            is_active=True
        ).first()
        if not session:
            try:
                raise NotFound(
                    detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                new_error(exc, request.user)

        stop_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    try:
        emulation_passed = request.data.get('emulation_passed', False)
    except Exception as exc:
        print('UTILS Exception', exc)
        new_error(exc, request.user)
        emulation_passed = False
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    if emulation_passed:
        experiment.experiment_flags = '101'
    else:
        experiment.experiment_flags = '100'
    experiment.save()

    generate_user_messages_for_emulation(request, experiment=experiment)


def active_emulation_to_wait_testbed_deploy(request, experiment: AerpawExperiment):
    """
    ACTIVE_EMULATION --> WAIT_TESTBED_DEPLOY
    - emulation complete
    - Flags 100 or 101

    @param: emulation_passed

    Session: update EMULATION --> end_date_time, ended_by, is_active=False
             create TESTBED --> created, created_by

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and stop
    session = OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    stop_experiment_session(session=session, user=request.user)

    # UPDATE STATE: wait_testbed_deploy
    try:
        emulation_passed = request.data.get('emulation_passed', False)
    except Exception as exc:
        print(exc)
        new_error(exc, request.user)
        emulation_passed = False
    if emulation_passed:
        # continue to wait_testbed_deploy
        experiment.experiment_flags = '101'
        experiment.is_emulation_required = False
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_DEPLOY
        experiment.save()
        # ACTION ITEMS:
        # create new TESTBED session
        create_experiment_session(
            session_type=OnDemandSession.SessionType.TESTBED,
            experiment=experiment,
            user=request.user
        )
        # MESSAGE / EMAIL: wait testbed deploy
        generate_user_messages_for_testbed(request=request, experiment=experiment)
    else:
        # send back to saved
        experiment.experiment_flags = '100'
        experiment.is_emulation_required = True
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
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
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    
    # get active SCHEDULED session and stop
    session = ScheduledSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ScheduledSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    end_scheduled_session(request=request, session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '010'
    experiment.save()

    reschedule = False if 'reschedule_session' not in request.data else request.data['reschedule_session']
    if str(reschedule) == 'True':
        new_session = saved_to_wait_testbed_schedule(request, experiment=experiment)

    # MESSAGE / EMAIL: active testbed to saved
    generate_user_messages_for_testbed(request=request, experiment=experiment)


def saved_to_wait_development_deploy(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_DEVELOPMENT_DEPLOY
    - start development session

    Session: create DEVELOPMENT --> created, created_by

    Permissions:
    - experimenter
    """
    # PREFLIGHT CHECK:
    # experiment has one or more resources
    if not experiment.resources.exists():
        try:
            raise ValidationError(
                detail="ValidationError: one or more resources required for /experiments/{0}/state".format(experiment.id))
        except ValidationError as exc:
            new_error(exc, request.user)
    # user has one or more credentials
    if not PublicCredentials.objects.filter(
            owner=request.user,
            is_deleted=False
    ).exists():
        try:
            raise ValidationError(
                detail="ValidationError: one or more user credentials required for /experiments/{0}/state".format(
                experiment.id))
        except ValidationError as exc:
            new_error(exc, request.user)

    # ACTION ITEMS:
    # lock experiment resources and experiment members from being further modified
    experiment.resources_locked = True
    experiment.members_locked = True
    experiment.save()
    # create new DEVELOPMENT session
    create_experiment_session(
        session_type=OnDemandSession.SessionType.DEVELOPMENT,
        experiment=experiment,
        user=request.user
    )

    # UPDATE STATE: wait_development_deploy
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY
    experiment.save()

    # MESSAGE / EMAIL: initiate development
    generate_user_messages_for_development(request=request, experiment=experiment)

    # PORTAL CF:
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # aerpaw ops: ap-cf-deploy-ve-exp.py
    command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-deploy-ve-exp_tut.py {0}".format(
        experiment.id)
    if MOCK_OPS:
        # DEVELOPMENT - always pass
        mock = True
        command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-deploy-ve-exp_cfdev.py {0}".format(
            experiment.id)
    else:
        # PRODUCTION
        mock = False
        
    print('mock= ', mock, command)
    aerpaw_thread = start_aerpaw_thread(request.user, experiment, AerpawThread.ThreadActions.INITIATE_DEV)
    ssh_thread = threading.Thread(target=wait_development_deploy, args=(request, experiment, command, mock, aerpaw_thread))
    ssh_thread.start()


def saved_to_wait_sandbox_deploy(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_SANDBOX_DEPLOY
    - schedule sandbox session

    Session: create SANDBOX --> created, created_by

    Permissions:
    - experimenter
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    try: 
        create_experiment_scheduled_session(
            session_type=ScheduledSession.SessionType.SANDBOX,
            experiment=experiment,
            scheduled_active_date=request.data.get('session_date'),
            user=request.user
        )
        
        # UPDATE STATE: wait_sandbox_deploy
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY
        experiment.save()
    except Exception as exc:
        new_error(exc, request.user)

    generate_user_messages_for_sandbox(request, experiment=experiment)

    # PORTAL CF: wait_sandbox_deploy
    # TODO: aerpaw ops: <SCRIPT> - placeholder for anticipated call
    command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-schedule-sbox_tut.py {0}".format(
        experiment.id)
    if MOCK_OPS:
        # DEVELOPMENT - always pass
        mock = True
        command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-schedule-sbox_cfdev.py {0}".format(
            experiment.id)
    else:
        # PRODUCTION
        mock = False
    aerpaw_thread = start_aerpaw_thread(request.user, experiment, AerpawThread.ThreadActions.INITIATE_SB)
    ssh_thread = threading.Thread(target=wait_sandbox_deploy, args=(request, experiment, command, mock, aerpaw_thread))
    ssh_thread.start()


def saved_to_wait_emulation_schedule(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_EMULATION_SCHEDULE
    - reqeust emulation session

    Session: create EMULATION --> created, created_by

    Permissions:
    - experimenter
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # create new EMULATION session
    try:
        is_ops_session = False if 'ops_session' not in request.data else request.data.get('ops_session')
        if is_ops_session == True:
            create_experiment_scheduled_session(
                session_type=ScheduledSession.SessionType.EMULATION,
                experiment=experiment,
                user=request.user
            )
        else:
            create_experiment_session(
                session_type=OnDemandSession.SessionType.EMULATION,
                experiment=experiment,
                user=request.user
            )

        # UPDATE STATE: wait_emulation_schedule
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE
        experiment.save()
    except Exception as exc:
        new_error(exc, request.user)

    generate_user_messages_for_emulation(request, experiment=experiment)


def saved_to_wait_testbed_schedule(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_TESTBED_SCHEDULE
    - request testbed session (allowed if (E&&P)|T

    Session: create TESTBED --> created, created_by

    Permissions:
    - experimenter
    """
    # PREFLIGHT CHECK:
    # Check if emulation is required first
    try:
        """ if is_emulation_required(experiment=experiment):
            wait_testbed_schedule_to_wait_emulation_schedule(request=request, experiment=experiment)
        else: """
        # ACTION ITEMS:
        # create new TESTBED session
        
        create_experiment_scheduled_session(
                session_type=ScheduledSession.SessionType.TESTBED,
                experiment=experiment,
                user=request.user,
            )
            
        

        # UPDATE STATE: wait_testbed_schedule
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE
        experiment.save()

        reschedule = False if 'reschedule_session' not in request.data else request.data.get('reschedule_session')
        if reschedule == 'True':
            scheduled_session = wait_testbed_schedule_to_wait_testbed_deploy(request, experiment=experiment)
    except Exception as exc:
        new_error(exc, request.user)

    # MESSAGE / EMAIL: submit to testbed - emulation not required
    generate_user_messages_for_testbed(request=request, experiment=experiment)

    # PORTAL CF: wait_testbed_schedule
    # TODO: Portal to manage next_state transition - normally this would be an Operator call
    # aerpaw ops: ap-cf-submit-to-tbed.py
    command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-submit-to-tbed_tut.py {0}".format(
            experiment.id)
    if MOCK_OPS:
        # DEVELOPMENT - always pass
        mock = True
        command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-submit-to-tbed_cfdev.py {0}".format(
            experiment.id)
    else:
        # PRODUCTION
        mock = False
        
    aerpaw_thread = start_aerpaw_thread(request.user, experiment, AerpawThread.ThreadActions.INITIATE_TB)
    ssh_thread = threading.Thread(target=wait_testbed_schedule, args=(request, experiment, command, mock, aerpaw_thread))
    ssh_thread.start()
    

def wait_development_deploy_to_active_development(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> ACTIVE_DEVELOPMENT
    - deployment on development VMs complete

    Session: update DEVELOPMENT --> start_date_time, started_by

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and start
    session = OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    # start session if not already running
    if not session.start_date_time:
        start_experiment_session(session=session, user=request.user)

    # UPDATE STATE: active_development
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_DEVELOPMENT
    experiment.experiment_flags = '000'
    experiment.save()

    # MESSAGE / EMAIL: active development session
    generate_user_messages_for_development(request=request, experiment=experiment)


def wait_development_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> SAVED
    - failure to deploy

    Session: update DEVELOPMENT --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.DEVELOPMENT,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    # stop session if it was previously running
    if session.start_date_time:
        stop_experiment_session(session=session, user=request.user)
    # otherwise cancel the session if it has not yet started
    else:
        cancel_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_emulation_deploy_to_active_emulation(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_DEPLOY --> ACTIVE_EMULATION
    - scheduled deployment of emulation complete

    Session: update EMULATION --> start_date_time, started_by
    Session Type: ScheduledSession

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active ScheduledSession and start
    if request.data['ops_session'] == True:
        ops_session = ScheduledSession.objects.filter(experiment = experiment, is_active = True).first()
        if not ops_session:
            try:
                raise NotFound(
                    detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                new_error(exc, request.user)
        started = start_scheduled_session(session = ops_session, user=request.user)
        
    else:
        # get active session and start

        session = OnDemandSession.objects.filter(
            experiment_id=experiment.id,
            session_type=OnDemandSession.SessionType.EMULATION,
            is_active=True
        ).first()
        if not session:
            try:
                raise NotFound(
                    detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                new_error(exc, request.user)
        start_experiment_session(session=session, user=request.user)

    # UPDATE STATE: active_emulation
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_EMULATION
    experiment.save()

    generate_user_messages_for_emulation(request, experiment=experiment)


def wait_emulation_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> SAVED
    - failure to deploy

    Session: update EMULATION --> active=False
    Session Type: ScheduledSession

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ScheduledSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ScheduledSession.SessionType.EMULATION,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    cancel_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.is_emulation_required = False
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()

    generate_user_messages_for_emulation(request, experiment=experiment)


def wait_emulation_schedule_to_wait_emulation_deploy(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_SCHEDULE --> WAIT_EMULATION_DEPLOY
    - schedule

    Session: update EMULATION --> active=True

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # no change to session

    #Schedule Emulation Deployment
    session = ScheduledSession.objects.filter(experiment = experiment, is_active = True).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    schedule_experiment_scheduled_session(request=request, session=session, user=request.user)

    # UPDATE STATE: wait_emulation_deploy
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_DEPLOY
    experiment.save()

    generate_user_messages_for_emulation(request, experiment=experiment)


def wait_emulation_schedule_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_SCHEDULE --> SAVED
    - cancel pending emulation session

    Session: update EMULATION --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    is_ops_session = False if 'ops_session' not in request.data else request.data.get('ops_session')
    if is_ops_session == True:
        ops_session = ScheduledSession.objects.filter(
                experiment=experiment, 
                session_type=ScheduledSession.SessionType.EMULATION, 
                is_active=True
            ).first()
        if not ops_session:
            try:
                raise NotFound(
                    detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                new_error(exc, request.user)

        cancel_scheduled_session(request=request, session=ops_session, user=request.user)
    else:
        session = OnDemandSession.objects.filter(
            experiment_id=experiment.id,
            session_type=OnDemandSession.SessionType.EMULATION,
            is_active=True
        ).first()
        if not session:
            try:
                raise NotFound(
                    detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                new_error(exc, request.user)

        cancel_experiment_session(session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.is_emulation_required = False
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()

    generate_user_messages_for_emulation(request, experiment=experiment)


def wait_sandbox_deploy_to_active_sandbox(request, experiment: AerpawExperiment):
    """
    WAIT_SANDBOX_DEPLOY --> ACTIVE_SANDBOX
    - scheduled deployment on sandbox complete

    Session: update SANDBOX --> start_date_time, started_by

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and start
    session = ScheduledSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ScheduledSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    # start session if not already running
    if not session.start_date_time:
        start_experiment_session(session=session, user=request.user)



    # UPDATE STATE: active_sandbox
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_SANDBOX
    experiment.experiment_flags = '000'
    experiment.save()

    user = experiment.created_by
    command = ''
    mock = False

    if MOCK_OPS:
        command = ''
        mock = True

    aerpaw_thread = start_aerpaw_thread(user, experiment, AerpawThread.ThreadActions.INITIATE_SB)
    ssh_thread = threading.Thread(target=active_sandbox, args=(experiment, command, mock, aerpaw_thread))
    ssh_thread.start()

    generate_user_messages_for_sandbox(request, experiment=experiment)


def wait_sandbox_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_SANDBOX_DEPLOY --> SAVED
    - cancel pending sandbox session

    Session: update SANDBOX --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ScheduledSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ScheduledSession.SessionType.SANDBOX,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    # stop session if it was previously running
    if session.start_date_time:
        end_scheduled_session(request, session=session, user=request.user)
    # otherwise cancel the session if it has not yet started
    else:
        cancel_scheduled_session(request, session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()

    generate_user_messages_for_sandbox(request, experiment=experiment)


def wait_testbed_deploy_to_active_testbed(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_DEPLOY --> ACTIVE_TESTBED
    - scheduled deployment of testbed complete

    Session: update TESTBED --> start_date_time, started_by

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    session = ScheduledSession.objects.filter(experiment = experiment, is_active = True).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    
    started = start_scheduled_session(session=session, user=request.user)

    # UPDATE STATE: active_testbed
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_TESTBED
    experiment.save()

    # MESSAGE / EMAIL: active testbed
    generate_user_messages_for_testbed(request=request, experiment=experiment)

    
def wait_testbed_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_DEPLOY --> SAVED
    - cancel

    Session: update TESTBED --> active=False

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ScheduledSession.objects.filter(
        experiment_id=experiment.id,
        session_type=ScheduledSession.SessionType.TESTBED,
        is_active=True
    ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    cancel_scheduled_session(request, session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '101'
    experiment.save()

    # MESSAGE / EMAIL: cancel testbed
    generate_user_messages_for_testbed(request=request, experiment=experiment)


def wait_testbed_schedule_to_wait_testbed_deploy(request, experiment: AerpawExperiment):
    print(f'\n wait_testbed_schedule_to_wait_testbed_deploy')
    """
    WAIT_TESTBED_SCHEDULE --> WAIT_TESTBED_DEPLOY
    - schedule

    Session: update TESTBED --> active=True

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # no change to session

    #Schedule Emulation Deployment
    session = ScheduledSession.objects.filter(experiment = experiment, is_active = True).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
    schedule_experiment_scheduled_session(request=request, session=session, user=request.user)

    # UPDATE STATE: wait_testbed_deploy
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_DEPLOY
    experiment.save()

    # MESSAGE / EMAIL: testbed execution has been scheduled
    generate_user_messages_for_testbed(request=request, experiment=experiment)

    
def wait_testbed_schedule_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_SCHEDULE --> SAVED
    - cancel pending testbed session

    Session: update TESTBED --> active=False

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session and cancel
    session = ScheduledSession.objects.filter(
            experiment=experiment, 
            session_type=ScheduledSession.SessionType.TESTBED, 
            is_active=True
        ).first()
    if not session:
        try:
            raise NotFound(
                detail="NotFound: unable to find active session for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            new_error(exc, request.user)
            
    cancel_scheduled_session(request=request, session=session, user=request.user)

    # UPDATE STATE: saved
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    if experiment.experiment_flags == '010':
        experiment.experiment_flags = '101'
    experiment.save()

    # MESSAGE / EMAIL: cancel testbed
    generate_user_messages_for_testbed(request=request, experiment=experiment)


def wait_testbed_schedule_to_wait_emulation_schedule(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_SCHEDULE --> WAIT_EMULATION_SCHEDULE
    - reroute to wait emulation schedule

    Session: create EMULATION --> created, created_by

    Permissions:
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    is_ops_session = False if 'ops_session' not in request.data else request.data.get('ops_session')
    if is_ops_session == True:
        create_experiment_scheduled_session(
            session_type=OnDemandSession.SessionType.EMULATION,
            experiment=experiment,
            user=request.user
        )
    else:
        # create new EMULATION session
        create_experiment_session(
            session_type=OnDemandSession.SessionType.EMULATION,
            experiment=experiment,
            user=request.user
        )

    # UPDATE STATE: wait_emulation_schedule
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE
    experiment.save()

    # MESSAGE / EMAIL: submit to testbed - emulation required
    generate_user_messages_for_testbed(request=request, experiment=experiment)


def same_to_same(request, experiment: AerpawExperiment):
    """
    Placeholder for same state update options

    Permissions:
    - experimenter OR
    - operator
    """
    # TODO: placeholder for same state update options
    # TODO: aerpaw ops: <SCRIPT> - placeholder for anticipated call
    # command = "sudo python3 /home/aerpawops/AERPAW-Dev/workflow-scripts/mock-tests/apcf_deploy_ve_exp_success.py {0}".format(
    #     experiment.id)
    # if MOCK_OPS:
    #     # DEVELOPMENT - always pass
    #     mock = True
    # else:
    #     # PRODUCTION
    #     mock = False
    # ssh_thread = threading.Thread(target=wait_development_deploy, args=(request, experiment, command, mock))
    # ssh_thread.start()


def saving_development(request, experiment: AerpawExperiment, command: str, exit_development: bool, mock: bool, aerpaw_thread: AerpawThread):
    
    exit_code = 0
    response = ''
    try:
        ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file, )
        response, exit_code = ssh_call.send_command(command, user=request.user, verbose=True, mock=mock)
        exit_code = exit_code
    except Exception as exc:
        response = exc
        error = new_error(exc, request.user)
        add_error_to_thread(aerpaw_thread, error)
        exit_code = 1
        

    
    """ if MOCK_OPS:
        # add sleep when using mock to simulate remote processing delay
        time.sleep(5)
        print('response: ' + str(response))
        print('exit code: ' + str(exit_code)) """

    # next state transition
    if exit_code == 0:
        if exit_development:
            # apcf_saveexit_ve_exp.py save-and-exit - success / failure
            # - saving_development --> saved
            saving_development_to_saved(request=request, experiment=experiment)
        else:
            # apcf_saveexit_ve_exp.py save - success
            # - saving_development --> active_development
            saving_development_to_active_development(request=request, experiment=experiment)
        end_aerpaw_thread(aerpaw_thread, exit_code, response)
    else:
        # - saving_development --> saved
        saving_development_to_saved(request=request, experiment=experiment)
        if exit_development:
            try:
                raise NotFound(
                    detail="SaveError: something occurred during the save for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                error = new_error(exc, request.user)
                add_error_to_thread(aerpaw_thread, error)
                end_aerpaw_thread(aerpaw_thread, exit_code, response)

        else:
            try:
                raise NotFound(
                    detail="SaveError: unable to deploy active_development for /experiments/{0}/state".format(
                        experiment.id))
            except NotFound as exc:
                error = new_error(exc, request.user)
                add_error_to_thread(aerpaw_thread, error)
                end_aerpaw_thread(aerpaw_thread, exit_code, response)
    
    
def saving_sandbox(request, experiment: AerpawExperiment, command: str, exit_sandbox: bool, mock: bool, aerpaw_thread: AerpawThread):
    # TODO: placeholder for save_sandbox
    response = '{"msg": "SaveSandbox: saving sandbox data", "urn": "/test"}'
    exit_code = 0
    # try:
    #   ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
    #   response, exit_code = ssh_call.send_command(command, verbose=True, mock=mock)
    # except Exception as exc:
    #   response = exc
    #   error = new_error(exc, request.user)
    #   add_error_to_thread(aerpaw_thread, error)
    #   exit_code = 1
    """ if MOCK_OPS:
        # add sleep when using mock to simulate remote processing delay
        time.sleep(5)
        print('response: ' + response)
        print('exit code: ' + str(exit_code)) """

    # next state transition
    if exit_code == 0:
        if exit_sandbox:
            # saving_sandbox --> saved
            saving_sandbox_to_saved(request=request, experiment=experiment)
        else:
            # saving_sandbox --> active_sandbox
            saving_sandbox_to_active_sandbox(request=request, experiment=experiment)
        end_aerpaw_thread(aerpaw_thread, exit_code, response)
    else:
        if exit_sandbox:
            try:
                raise NotFound(
                    detail="SaveError: something occurred during the save for /experiments/{0}/state".format(experiment.id))
            except NotFound as exc:
                error = new_error(exc, request.user)
                add_error_to_thread(aerpaw_thread, error)
                end_aerpaw_thread(aerpaw_thread, exit_code, response)

        else:
            try:
                raise NotFound(
                    detail="SaveError: unable to deploy active_sandbox for /experiments/{0}/state".format(
                        experiment.id))
            except NotFound as exc:
                error = new_error(exc, request.user)
                add_error_to_thread(aerpaw_thread, error)
                end_aerpaw_thread(aerpaw_thread, exit_code, response)


def wait_development_deploy(request, experiment: AerpawExperiment, command: str, mock: bool, aerpaw_thread: AerpawThread) -> None:
    
    exit_code = 0
    response = ''
    try:
        ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
        response, exit_code = ssh_call.send_command(command, verbose=True, mock=mock)
    except Exception as exc:
        print(f'Excpetion in wait_development_deploy:\n {exc}\n')
        response = exc
        error = new_error(exc, request.user)
        add_error_to_thread(aerpaw_thread, error)
        exit_code = 1

    """ if MOCK_OPS:
        # add sleep when using mock to simulate remote processing delay
        time.sleep(10)
        print('response: ' + str(response))
        print('exit code: ' + str(exit_code)) """

    # next state transition
    if exit_code == 0:
        # apcf_deploy_ve_exp - success
        # - wait_development_deploy --> active_development
        wait_development_deploy_to_active_development(request=request, experiment=experiment)
        end_aerpaw_thread(aerpaw_thread, exit_code, response)
    else:
        # apcf_deploy_ve_exp - failure
        # - wait_development_deploy --> saved
        wait_development_deploy_to_saved(request=request, experiment=experiment)
        try:
            raise NotFound(
                detail="DeployError: unable to deploy active_development for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
                error = new_error(exc, request.user)
                add_error_to_thread(aerpaw_thread, error)
                end_aerpaw_thread(aerpaw_thread, exit_code, response)


def wait_sandbox_deploy(request, experiment: AerpawExperiment, command: str, mock: bool, aerpaw_thread: AerpawThread):
    # TODO: placeholder for wait_sandbox_deploy
    response = '{"msg": "WaitSandboxDeploy: deploying sandbox", "urn": "/test"}'
    exit_code = 0

    # try:
    #   ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
    #   response, exit_code = ssh_call.send_command(command, verbose=True, mock=mock)
    #   
    # except Exception as exc:
    #    response = exc
    #    error = new_error(exc, request.user)
    #    add_error_to_thread(aerpaw_thread, error)
    #    exit_code = 1


    """ if MOCK_OPS:
        # add sleep when using mock to simulate remote processing delay
        time.sleep(10)
        print('response: ' + response)
        print('exit code: ' + str(exit_code)) """

    # next state transition
    if exit_code == 0:
        # ?? This will be a cronjob or JS setInterval function: wait_sandbox_deploy --> active_sandbox ??
        # wait_sandbox_deploy_to_active_sandbox(request=request, experiment=experiment)
        end_aerpaw_thread(aerpaw_thread, exit_code, response)
    else:
        # - wait_sandbox_deploy --> saved
        wait_sandbox_deploy_to_saved(request=request, experiment=experiment)
        try:
            raise NotFound(
                detail="DeployError: unable to deploy active_sandbox for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
            error = new_error(exc, request.user)
            add_error_to_thread(aerpaw_thread, error)
            end_aerpaw_thread(aerpaw_thread, exit_code, response)

def active_sandbox(experiment: AerpawExperiment, command: str, mock: bool, aerpaw_thread: AerpawThread):
    print('function for deploying sandbox is still being written')
    exit_code = 0
    response = ''
    try:
        ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
        response, exit_code = ssh_call.send_command(command, verbose=True, mock=mock)
    except Exception as exc:
        print(f'Excpetion in wait_development_deploy:\n {exc}\n')
        response = exc
        error = new_error(exc, experiment.created_by)
        add_error_to_thread(aerpaw_thread, error)
        exit_code = 1

    """ if MOCK_OPS:
        # add sleep when using mock to simulate remote processing delay
        time.sleep(10)
        print('response: ' + str(response))
        print('exit code: ' + str(exit_code)) """

    # next state transition
    if exit_code == 0:
        # apcf_deploy_ve_exp - success
        # - wait_sandbox_deploy --> active_sandbox
        
        end_aerpaw_thread(aerpaw_thread, exit_code, response)
    else:
        # apcf_deploy_ve_exp - failure
        # - wait_sandbox_deploy --> saved
        wait_sandbox_deploy_to_saved(experiment=experiment)
        try:
            raise NotFound(
                detail="DeployError: unable to deploy active_sandbox for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
                error = new_error(exc, experiment.created_by)
                add_error_to_thread(aerpaw_thread, error)
                end_aerpaw_thread(aerpaw_thread, exit_code, response)


def is_emulation_required(experiment: AerpawExperiment) -> bool:
    if experiment.experiment_flags in ['101', '010']:
        # wait_testbed_schedule
        experiment.is_emulation_required = False
    else:
        # wait_emulation_schedule
        experiment.is_emulation_required = True

    experiment.save()
    return experiment.is_emulation_required


def wait_testbed_schedule(request, experiment: AerpawExperiment, command: str, mock: bool, aerpaw_thread: AerpawThread) -> None:
    
    exit_code = 0
    response = ''
    try:
        ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
        response, exit_code = ssh_call.send_command(command, verbose=True, mock=mock)
    except Exception as exc:
        print(f'Excpetion in wait_testbed_schedule:\n {exc}\n')
        response = exc
        error = new_error(exc, request.user)
        add_error_to_thread(aerpaw_thread, error)
        exit_code = 1

    """ if MOCK_OPS:
        # add sleep when using mock to simulate remote processing delay
        time.sleep(10)
        print('response: ' + str(response))
        print('exit code: ' + str(exit_code)) """

    # TODO: determine if any transition should take place based on return value of script
    # next state transition
    if exit_code == 0:
        # ap-cf-submit-to-tbed.py - success
        # - do nothing
        print(exit_code)
        end_aerpaw_thread(aerpaw_thread, exit_code, response)
    else:
        # ap-cf-submit-to-tbed.py- failure
        # - do nothing
        print(exit_code)
        try:
            raise NotFound(
                detail="DeployError: unable to deploy active_testbed for /experiments/{0}/state".format(experiment.id))
        except NotFound as exc:
                error = new_error(exc, request.user)
                add_error_to_thread(aerpaw_thread, error)
                end_aerpaw_thread(aerpaw_thread, exit_code, response)


def retired(request, experiment: AerpawExperiment, command: str, mock: bool, aerpaw_thread: AerpawThread) -> None:
    exit_code = 0
    response = ''
    try:
        ssh_call = AerpawSsh(hostname=aerpaw_ops_host, username=aerpaw_ops_user, keyfile=aerpaw_ops_key_file)
        response, exit_code = ssh_call.send_command(command, verbose=True, mock=mock)
    except Exception as exc:
        print(exc)
        response = exc
        error = new_error(exc, request.user)
        add_error_to_thread(aerpaw_thread, error)
        exit_code = 1
    
    """ if MOCK_OPS:
        # add sleep when using mock to simulate remote processing delay
        time.sleep(10)
        print('response: ' + str(response))
        print('exit code: ' + str(exit_code)) """

    # TODO: determine if any transition should take place based on return value of script
    # next state transition
    if exit_code == 0:
        # ap-cf-retire-exp.py - success
        # - do nothing
        print('exit code: ', exit_code)
        end_aerpaw_thread(aerpaw_thread, exit_code, response)
    else:
        # ap-cf-retire-exp.py- failure
        # - do nothing
        print('exit code: ', exit_code)
        experiment.is_retired = False
        experiment.save()
        try:
            raise NotFound(
                detail="RetireError: unable to retire experiment /experiments/{0}".format(experiment.id))
        except NotFound as exc:
                error = new_error(exc, request.user)
                add_error_to_thread(aerpaw_thread, error)
                end_aerpaw_thread(aerpaw_thread, exit_code, response)


def to_retired(request, experiment: AerpawExperiment):
    """
    ANY --> SAVED
    - active_development --> saved && active_sandbox --> saved are not valid transitions according to the experiment_states api
    - Things to do:
      - Get current state -- Should be able to just check experiment.state
      - Exit development/sandbox if state == active_development or active_sandbox
      - Save experiment
      - Find APVESN of the experiment		This and the step below need to be their own cf script
      - Run ap-teardown-virtual-experiment.sh <canNum> <resources> to cleanup experiment containers on APVESN
      - Cleanup DHCP & OVPN configs on VPN server
      - Set experiment to retired
      - (Optional) Send message

    Session: update DEVELOPMENT --> no change		#????

    Permissions:
    - experimenter OR
    - operator
    """
    # PREFLIGHT CHECK:

    # ACTION ITEMS:
    # get active session
    session = OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.DEVELOPMENT.value,
        start_date_time__isnull=False,
        started_by__isnull=False,
        end_date_time__isnull=False,
        ended_by__isnull=False
    ).order_by('-created').exists()

    print('session = ', session)
    if not session:
        try:
            response = f'Experiment {experiment.id} is successfully enjoying retirement!'
            aerpaw_thread = start_aerpaw_thread(request.user, experiment, AerpawThread.ThreadActions.RETIRE)
            end_aerpaw_thread(aerpaw_thread, 0, response)
            return True
        except Exception as exc:
            new_error(exc, request.user)
            return False

    print('experiment.experiment_state = ', experiment.experiment_state)
    # UPDATE STATE: save_development if current state is ACTIVE_DEVELOPMENT
    if experiment.experiment_state == AerpawExperiment.ExperimentState.ACTIVE_DEVELOPMENT:
        request.data.exit_development = True
        active_development_to_saving_development(request, experiment=experiment)
    # UPDATE STATE: save_sandbox if current state is ACTIVE_SANDBOX
    elif experiment.experiment_state == AerpawExperiment.ExperimentState.ACTIVE_SANDBOX:
        request.data.exit_sandbox = True
        active_sandbox_to_saving_sandbox(request, experiment=experiment)
    # UPDATE STATE: saved if current state is ACTIVE_EMULATION
    elif experiment.experiment_state == AerpawExperiment.ExperimentState.ACTIVE_EMULATION:
        request.data.emulation_passed = False
        active_emulation_to_saved(request, experiment=experiment)
    # UPDATE STATE: saved if current state is ACTIVE_TESTBED
    elif experiment.experiment_state == AerpawExperiment.ExperimentState.ACTIVE_TESTBED:
        active_testbed_to_saved(request, experiment=experiment)
    # UPDATE STATE: saved (for all other cases)
    if experiment.experiment_state != AerpawExperiment.ExperimentState.SAVED:
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.experiment_flags = '000'
        experiment.save()

    # Invoke retire script to cleanup all experiment files
    command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-retire-exp_tut.py {0}".format(
           experiment.id)
    if MOCK_OPS:
        # DEVELOPMENT - always pass
        mock = True
        command = "sudo python3 /home/aerpawops/AERPAW-Dev/DCS/platform_control/utils/ap-cf-ops-retire-exp_cfdev.py {0}".format(
           experiment.id)
    else:
        # PRODUCTION
        mock = False
    print('command = ', command)
    print('Mock = ', mock)
    aerpaw_thread = start_aerpaw_thread(request.user, experiment, AerpawThread.ThreadActions.RETIRE)
    ssh_thread = threading.Thread(target=retired, args=(request, experiment, command, mock, aerpaw_thread))
    ssh_thread.start()





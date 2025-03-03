from datetime import datetime
from django.http import HttpRequest
from rest_framework.request import Request

from portal.apps.credentials.models import PublicCredentials
from portal.apps.experiment_info.form_dashboard import new_field_trip
from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.experiments.api.viewsets import ExperimentViewSet
from portal.apps.experiments.models import AerpawExperiment, OnDemandSession, ScheduledSession
from portal.apps.users.models import AerpawUser
from portal.apps.resources.models import AerpawResource
from portal.apps.experiments.api.experiment_states import next_natural_transition
from portal.apps.experiments.api.experiment_sessions import schedule_experiment_scheduled_session, start_scheduled_session


def check_initiate_development(user: AerpawUser, experiment: AerpawExperiment):
    # TODO: define checks for initiate development
    # experiment has one or more resources
    if not experiment.resources.exists():
        return False
    # user has one or more public keys
    if not PublicCredentials.objects.filter(
            owner=user,
            is_deleted=False
    ).exists():
        return False
    return True


def check_submit_to_sandbox(user: AerpawUser, experiment: AerpawExperiment):
    # TODO: define checks for submit to sandbox
    # user has one or more public keys
    """  
    Sandbox environment has access to limited resources:
        4 - Fixed Nodes
        2 - Large Portable Node
        2 - Small Portable Node

    Experiments with more resources than listed above are unable to access the sandbox environment

    Resources:
        AFRN = AERPAW Fixed Radio Node
        APRN = AERPAW Portable Radio Node
        UAV = Unmanned Aerial Vehicle
        UGV = Unmanned Ground Vehicle
        THREE_PBBE = Third-Party Black-Box Equipment (Non-Canonical Experiments Only)
        OTHER = 
    """
    if not PublicCredentials.objects.filter(
            owner=user,
            is_deleted=False
    ).exists():
        return False
    
    if experiment.experiment_state != 'saved':
        return False
    
    if not experiment.resources.exists():
        return False
    
    if experiment.resources.count() > 8:
        return False
    
    fixed_nodes = 0
    LPNs = 0
    SPNs = 0
    for resource in experiment.resources.all():
        print(f'LPNS= {resource.name[:3]}')
        print(f'SPNS= {resource.name[:3]}')
        if resource.resource_type == 'AFRN':
            fixed_nodes += 1
        elif resource.resource_type == 'APRN' and resource.name[:3] =='LPN':
            LPNs += 1
        elif resource.resource_type == 'APRN' and resource.name[:3] =='SPN':
            SPNs += 1
        print(f'# of LPNS= {LPNs}')
        print(f'# of SPNS= {SPNs}')
    if fixed_nodes > 4:
        return False
    if LPNs > 2:
        return False
    if SPNs > 2:
        return False
    
    # experiment has completed at least one successful development cycle
    if not OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.DEVELOPMENT.value,
        start_date_time__isnull=False,
        started_by__isnull=False,
        end_date_time__isnull=False,
        ended_by__isnull=False
    ).order_by('-created').exists():
        return False
    
    return True


def check_submit_to_emulation(user: AerpawUser, experiment: AerpawExperiment):
    # TODO: define checks for submit to emulation
    # user has one or more public keys

    
    #if not PublicCredentials.objects.filter(
    #        owner=user,
    #        is_deleted=False
    #).exists():
    #    return False
    if user.is_operator() == False:
        return False
    # experiment has completed at least one successful development cycle
    
    if not OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.DEVELOPMENT.value,
        start_date_time__isnull=False,
        started_by__isnull=False,
        end_date_time__isnull=False,
        ended_by__isnull=False
    ).order_by('-created').exists():
        return False
    
    return True


def check_submit_to_testbed(user: AerpawUser, experiment: AerpawExperiment):
    """
    Experiment has completed at least one successful development cycle at any point in time
    - TODO: consider checking for most recent development session being successful
    """
    # TODO: define checks for submit to testbed
    # experiment has one or more resources
    
    if not experiment.resources.exists():
        return False
    # user has one or more public keys
    if not PublicCredentials.objects.filter(
            owner=user,
            is_deleted=False
    ).exists():
        return False
    # experiment has completed at least one successful development cycle
    if not OnDemandSession.objects.filter(
        experiment_id=experiment.id,
        session_type=OnDemandSession.SessionType.DEVELOPMENT.value,
        start_date_time__isnull=False,
        started_by__isnull=False,
        end_date_time__isnull=False,
        ended_by__isnull=False
    ).order_by('-created').exists():
        return False
    return True


def get_dashboard_buttons(request, experiment_id: int) -> dict:
    """
    - ACTIVE_DEVELOPMENT       - Save, Save & Exit
    - ACTIVE_EMULATION         - n/a
    - ACTIVE_SANDBOX           - Save, Save & Exit
    - ACTIVE_TESTBED           - n/a
    - SAVED                    - Initiate Development, Submit to Sandbox, Submit to Emulation, Submit to Testbed
    - SAVING_DEVELOPMENT       - n/a
    - SAVING_SANDBOX           - n/a
    - WAIT_DEVELOPMENT_DEPLOY  - n/a
    - WAIT_EMULATION_DEPLOY    - Cancel
    - WAIT_EMULATION_SCHEDULE  - Cancel
    - WAIT_SANDBOX_DEPLOY      - Cancel
    - WAIT_TESTBED_DEPLOY      - Cancel
    - WAIT_TESTBED_SCHEDULE    - Cancel
    """

    buttons = {
        'b_dev_init': False,
        'b_dev_save': False,
        'b_dev_save_exit': False,
        'b_sandbox_submit': False,
        'b_sandbox_cancel': False,
        'b_sandbox_save': False,
        'b_sandbox_save_exit': False,
        'b_emu_submit': False,
        'b_emu_cancel': False,
        'b_testbed_submit': False,
        'b_testbed_cancel': False
    }
    
    try:
        user = request.user
        experiment = AerpawExperiment.objects.get(id=experiment_id)

        # ensure user is a member of the experiment, or the creator of the experiment
        if not experiment.is_member(user=user) and not experiment.is_creator(user=user):
            # user is not a member and not the creator - return all buttons set to False
            return buttons

        # is_retired or is_deleted
        if experiment.is_retired or experiment.is_deleted:
            return buttons

        # ACTIVE_DEVELOPMENT       - Save, Save & Exit
        if experiment.experiment_state == AerpawExperiment.ExperimentState.ACTIVE_DEVELOPMENT:
            buttons['b_dev_save'] = True
            buttons['b_dev_save_exit'] = True
        # ACTIVE_EMULATION         - n/a
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.ACTIVE_EMULATION:
            pass
        # ACTIVE_SANDBOX           - Save, Save & Exit
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.ACTIVE_SANDBOX:
            buttons['b_sandbox_save'] = True
            buttons['b_sandbox_save_exit'] = True
        # ACTIVE_TESTBED           - n/a
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.ACTIVE_TESTBED:
            pass
        # SAVED                    - Initiate Development, Submit to Sandbox, Submit to Emulation, Submit to Testbed
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.SAVED:
            # initiate development
            buttons['b_dev_init'] = check_initiate_development(user=user, experiment=experiment)
            # submit to sandbox
            buttons['b_sandbox_submit'] = check_submit_to_sandbox(user=user, experiment=experiment)
            # submit to emulation
            buttons['b_emu_submit'] = check_submit_to_emulation(user=user, experiment=experiment)
            # submit to testbed
            buttons['b_testbed_submit'] = check_submit_to_testbed(user=user, experiment=experiment)
        # SAVING_DEVELOPMENT  - n/a
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.SAVING_DEVELOPMENT:
            pass
        # SAVING_SANDBOX  - n/a
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.SAVING_SANDBOX:
            pass
        # WAIT_DEVELOPMENT_DEPLOY  - n/a
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY:
            pass
        # WAIT_EMULATION_DEPLOY    - Cancel
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.WAIT_EMULATION_DEPLOY:
            buttons['b_emu_cancel'] = True
        # WAIT_EMULATION_SCHEDULE  - Cancel
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE:
            buttons['b_emu_cancel'] = True
        # WAIT_SANDBOX_DEPLOY      - Cancel
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY:
            buttons['b_sandbox_cancel'] = True
        # WAIT_TESTBED_DEPLOY      - Cancel
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.WAIT_TESTBED_DEPLOY:
            buttons['b_testbed_cancel'] = True
        # WAIT_TESTBED_SCHEDULE    - Cancel
        elif experiment.experiment_state == AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE:
            buttons['b_testbed_cancel'] = True
        else:
            pass

        return buttons

    except Exception as exc:
        print(exc)
        new_error(exc, request.user)
        return buttons


def evaluate_dashboard_action(request):
    api_request = Request(request=HttpRequest())
    api_request.user = request.user
    api_request.method = 'PUT'
    e = ExperimentViewSet(request=api_request)
    op = None

    try:
        if request.POST.get('b_dev_init'):
            experiment_id = request.POST.get('b_dev_init')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_dev_save'):
            experiment_id = request.POST.get('b_dev_save')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVING_DEVELOPMENT})
            api_request.data.update({'exit_development': False})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_dev_save_exit'):
            experiment_id = request.POST.get('b_dev_save_exit')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVING_DEVELOPMENT})
            api_request.data.update({'exit_development': True})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_sandbox_submit'):
            print('request.POST', request.POST)
            print(f'session date type= {type(request.POST.get("sandbox-calendar-day"))}: {request.POST.get("sandbox-calendar-day")}')
            experiment_id = request.POST.get('b_sandbox_submit')
            api_request.data.update({
                'next_state': AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY,
                'ops_session':True,
                'session_date': request.POST.getlist('sandbox-calendar-day')
                })
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_sandbox_cancel'):
            experiment_id = request.POST.get('b_sandbox_cancel')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVED})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_sandbox_save'):
            experiment_id = request.POST.get('b_sandbox_save')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVING_SANDBOX})
            api_request.data.update({'exit_sandbox': False})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_sandbox_save_exit'):
            experiment_id = request.POST.get('b_sandbox_save_exit')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVING_SANDBOX})
            api_request.data.update({'exit_sandbox': True})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_emu_submit'):
            experiment_id = request.POST.get('b_emu_submit')
            api_request.data.update({
                'next_state': AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE,
                'ops_session': True,
                })
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_emu_cancel'):
            experiment_id = request.POST.get('b_emu_cancel')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVED})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_testbed_submit'):
            experiment_id = request.POST.get('b_testbed_submit')
            api_request.data.update({
                'next_state': AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE,
                'ops_session': True,
                })
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_testbed_cancel'):
            experiment_id = request.POST.get('b_testbed_cancel')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVED})
            op = e.state(api_request, pk=int(experiment_id))

    except Exception as exc:
        print(f'Evaluate Dashbord Actions Exception= {exc}')
        new_error(exc, request.user)


def evaluate_session_dashboard_action(request):
    print('DASHBOARD evaluate_session_dashboard_action')
    print('request.POST', request.POST)
    api_request = Request(request=HttpRequest())
    api_request.user = request.user
    api_request.method = 'PUT'
    e = ExperimentViewSet(request=api_request)
    op = None
    if request.POST.get('end_session'):
        experiment = AerpawExperiment.objects.get(id = request.POST.get('end_session'))
        try:
            session_type = ScheduledSession.objects.filter(experiment=experiment).order_by('-created').first().session_type
        except:
            session_type = OnDemandSession.objects.filter(experiment=experiment).order_by('-created').first().session_type
        
        if session_type == 'sandbox':
            next_state = AerpawExperiment.ExperimentState.SAVING_SANDBOX
        else:
            next_state = AerpawExperiment.ExperimentState.SAVED
        
        is_success = False
        if request.POST.get('session_success') and request.POST.get('session_success') == 'True':
            is_success = True
        api_request.data.update({
            'next_state': next_state,
            'ops_session':True,
            'session_description': request.POST.get('session_description'),
            'is_success': is_success,
            'reschedule_session': request.POST.get('reschedule_session') if request.POST.get('reschedule_session') else False,
            'session_datetime': request.POST.get("session_datetime") if request.POST.get('session_datetime') else None,
            'experiment': experiment,
            })
        op = e.state(api_request, pk=int(experiment.id))

    # Ends testbed session and initiates a new development session
    if request.POST.get('end_testbed_initiate_dev'):
        print('Ending testbed session and starting a new dev session')
        print(f'request.POST= {request.POST}')
        experiment = AerpawExperiment.objects.get(id=request.POST.get('end_testbed_initiate_dev'))
        api_request.data.update(request.POST)
        api_request.data.update({
            'experiment_id':experiment.id,
            'next_state': AerpawExperiment.ExperimentState.SAVED,
            'session_description':request.POST.get('comments'),
            'is_success': request.POST.get('session_success'),
            'experiment':experiment
            })
        # Save the testbed session and the field trip
        op = e.state(api_request, pk=int(experiment.id))
        new_field_trip(api_request)

        # Initiate a new development session
        api_request.data.update({'next_state':AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY})
        op = e.state(api_request, pk=int(experiment.id))

        

    # Ends Testbed session and does NOT intiate a new development session
    if request.POST.get('end_testbed_only'):
        print('Ending testbed session without starting a new dev session')
        print(f'request.POST= {request.POST}')
        api_request.data.update(**request.POST)
        api_request.data.update({'experiment_id':request.POST.get('end_testbed_only')})
        new_field_trip(api_request)

    if request.POST.get('new_development'):
        experiment_id = request.POST.get('new_development')
        api_request.data.update({
            'next_state': AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY,
            'ops_session':False
            })
        op = e.state(api_request, pk=int(experiment_id))
    if request.POST.get('new_sandbox'):
        experiment_id = request.POST.get('new_sandbox')
        api_request.data.update({
            'next_state': AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY,
            'ops_session':True
            })
        op = e.state(api_request, pk=int(experiment_id))
    if request.POST.get('new_emulation'):
        experiment_id = request.POST.get('new_emulation')
        api_request.data.update({
            'next_state': AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE,
            'ops_session':True
            })
        op = e.state(api_request, pk=int(experiment_id))
    if request.POST.get('new_testbed'):
        experiment_id = request.POST.get('new_testbed')
        api_request.data.update({
            'next_state': AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE,
            'ops_session':True
            })
        op = e.state(api_request, pk=int(experiment_id))
    if request.POST.get('schedule_session'):
        experiment = AerpawExperiment.objects.get(id = request.POST.get('schedule_session'))
        next_state = next_natural_transition(experiment)
        api_request.data.update({
            'next_state': AerpawExperiment.ExperimentState(next_state),
            'session_datetime':request.POST.get('session_datetime'),
            })
        op = e.state(api_request, pk=int(experiment.id))


    if request.POST.get('start_session'):
        print('start_session')
        experiment = AerpawExperiment.objects.get(id = request.POST.get('start_session'))
        next_state = next_natural_transition(experiment)
        api_request.data.update({
            'next_state': AerpawExperiment.ExperimentState(next_state),
            'ops_session':True
            })
        op = e.state(api_request, pk=int(experiment.id))

    if request.POST.get('cancel_session'):
        print('cancel_session')
        experiment = AerpawExperiment.objects.get(id = request.POST.get('cancel_session'))
        is_success = False
        if request.POST.get('session_success') and request.POST.get('session_success') == 'True':
            is_success = True
        api_request.data.update({
            'next_state': AerpawExperiment.ExperimentState.SAVED,
            'ops_session':True,
            'session_description': request.POST.get('session_description'),
            'is_success': is_success,
            })
        op = e.state(api_request, pk=int(experiment.id))

        if request.POST.get('reschedule_session') and request.POST.get('reschedule_session') == 'True':
            print('Rescheduling Session')
        

def get_session_dashboard_buttons(request, session_id: int) -> dict:

    buttons = {
        'start': False,
        'end': False,
        'schedule': False,
        'no_actions': False,
    }

    if not session_id:
        return buttons
    else:
        try:
            try: 
                session = ScheduledSession.objects.select_related('experiment').get(id=session_id)
            except:
                session = OnDemandSession.objects.select_related('experiment').get(id=session_id)

            buttons['session_id'] = session.id
            if session.experiment.experiment_state == 'wait_development_deploy':
                buttons['no_actions'] = True

            elif session.experiment.experiment_state == 'active_development':
                buttons['no_actions'] = True

            elif session.experiment.experiment_state == 'wait_sandbox_deploy':
                buttons['start'] = True
                buttons['end'] = True

            elif session.experiment.experiment_state == 'active_sandbox':
                buttons['no_actions'] = True

            elif session.experiment.experiment_state == 'wait_emulation_schedule':
                buttons['schedule'] = True
                buttons['end'] = True

            elif session.experiment.experiment_state == 'wait_emulation_deploy':
                buttons['start'] = True
                buttons['end'] = True

            elif session.experiment.experiment_state == 'active_emulation':
                buttons['end'] = True

            elif session.experiment.experiment_state == 'wait_testbed_schedule':
                buttons['schedule'] = True
                buttons['end'] = True

            elif session.experiment.experiment_state == 'wait_testbed_deploy':
                buttons['start'] = True
                buttons['end'] = True

            elif session.experiment.experiment_state == 'active_testbed':
                buttons['end'] = True

            elif session.experiment.experiment_state == 'saved':
                buttons['no_actions'] = True

            else:
                buttons['no_actions'] = True
            return buttons
                
        except Exception as exc:
            print(exc)
            new_error(exc, request.user)
            buttons['no_actions'] = True
            return buttons
        

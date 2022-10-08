from django.http import HttpRequest
from rest_framework.request import Request

from portal.apps.credentials.models import PublicCredentials
from portal.apps.experiments.api.viewsets import ExperimentViewSet
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser


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


def check_submit_to_sandbox():
    # TODO: define checks for submit to sandbox
    return False


def check_submit_to_emulation():
    # TODO: define checks for submit to emulation
    return False


def check_submit_to_testbed(experiment: AerpawExperiment):
    # TODO: define checks for submit to testbed
    if experiment.experiment_flags == '101':
        return True
    else:
        return False


def get_dashboard_buttons(request, experiment_id: int) -> dict:
    """
    - ACTIVE_DEVELOPMENT       - Save, Save & Exit
    - ACTIVE_EMULATION         - n/a
    - ACTIVE_SANDBOX           - Save, Save & Exit
    - ACTIVE_TESTBED           - n/a
    - SAVED                    - Initiate Development, Submit to Sandbox, Submit to Emulation, Submit to Testbed
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
            buttons['b_sandbox_submit'] = check_submit_to_sandbox()
            # submit to emulation
            buttons['b_emu_submit'] = check_submit_to_emulation()
            # submit to testbed
            buttons['b_testbed_submit'] = check_submit_to_testbed(experiment=experiment)
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
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVE_DEVELOPMENT})
            api_request.data.update({'exit_development': False})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_dev_save_exit'):
            experiment_id = request.POST.get('b_dev_save_exit')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVE_DEVELOPMENT})
            api_request.data.update({'exit_development': True})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_sandbox_submit'):
            experiment_id = request.POST.get('b_sandbox_submit')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_sandbox_cancel'):
            experiment_id = request.POST.get('b_sandbox_cancel')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVED})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_sandbox_save'):
            experiment_id = request.POST.get('b_sandbox_save')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVE_SANDBOX})
            api_request.data.update({'exit_sandbox': False})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_sandbox_save_exit'):
            experiment_id = request.POST.get('b_sandbox_save_exit')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVE_SANDBOX})
            api_request.data.update({'exit_sandbox': True})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_emu_submit'):
            experiment_id = request.POST.get('b_emu_submit')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_emu_cancel'):
            experiment_id = request.POST.get('b_emu_cancel')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVED})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_testbed_submit'):
            experiment_id = request.POST.get('b_testbed_submit')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE})
            op = e.state(api_request, pk=int(experiment_id))
        if request.POST.get('b_testbed_cancel'):
            experiment_id = request.POST.get('b_testbed_cancel')
            api_request.data.update({'next_state': AerpawExperiment.ExperimentState.SAVED})
            op = e.state(api_request, pk=int(experiment_id))

    except Exception as exc:
        print(exc)

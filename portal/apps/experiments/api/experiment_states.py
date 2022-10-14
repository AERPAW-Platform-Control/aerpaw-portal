from portal.apps.experiments.api.experiment_utils import active_development_to_saving_development, \
    active_emulation_to_saved, active_sandbox_to_saving_sandbox, active_testbed_to_saved, same_to_same, \
    saved_to_wait_development_deploy, saved_to_wait_emulation_schedule, saved_to_wait_sandbox_deploy, \
    saved_to_wait_testbed_schedule, saving_development_to_active_development, saving_development_to_saved, \
    saving_sandbox_to_active_sandbox, saving_sandbox_to_saved, wait_development_deploy_to_active_development, \
    wait_development_deploy_to_saved, wait_emulation_deploy_to_active_emulation, wait_emulation_deploy_to_saved, \
    wait_emulation_schedule_to_saved, wait_emulation_schedule_to_wait_emulation_deploy, \
    wait_sandbox_deploy_to_active_sandbox, wait_sandbox_deploy_to_saved, wait_testbed_deploy_to_active_testbed, \
    wait_testbed_deploy_to_saved, wait_testbed_schedule_to_saved, wait_testbed_schedule_to_wait_testbed_deploy
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser

"""
Valid experiment transition states
- ref: https://user-images.githubusercontent.com/5332509/186757199-86f44e94-e590-4e1d-9763-5f8401c69b5d.png
"""
_VALID_EXPERIMENTER_TRANSITION = [
    ('active_development', 'saving_development'),
    ('active_sandbox', 'saving_sandbox'),
    ('saving_development', 'saved'),
    ('saving_sandbox', 'saved'),
    ('saved', 'wait_development_deploy'),
    ('saved', 'wait_sandbox_deploy'),
    ('saved', 'wait_emulation_schedule'),
    ('saved', 'wait_testbed_schedule'),
    ('wait_development_deploy', 'saved'),
    ('wait_emulation_deploy', 'saved'),
    ('wait_emulation_schedule', 'wait_emulation_deploy'),
    ('wait_emulation_schedule', 'saved'),
    ('wait_sandbox_deploy', 'saved'),
    ('wait_testbed_deploy', 'saved'),
    ('wait_testbed_schedule', 'saved')
]

_VALID_OPERATOR_TRANSITION = [
    ('active_development', 'saving_development'),
    ('active_emulation', 'saved'),
    ('active_sandbox', 'saving_sandbox'),
    ('active_testbed', 'saved'),
    ('saving_development', 'saved'),
    ('saving_development', 'active_development'),
    ('saving_sandbox', 'saved'),
    ('saving_sandbox', 'active_sandbox'),
    ('wait_development_deploy', 'active_development'),
    ('wait_development_deploy', 'saved'),
    ('wait_emulation_deploy', 'active_emulation'),
    ('wait_emulation_deploy', 'saved'),
    ('wait_emulation_schedule', 'wait_emulation_deploy'),
    ('wait_emulation_schedule', 'saved'),
    ('wait_sandbox_deploy', 'active_sandbox'),
    ('wait_sandbox_deploy', 'saved'),
    ('wait_testbed_deploy', 'active_testbed'),
    ('wait_testbed_deploy', 'saved'),
    ('wait_testbed_schedule', 'wait_testbed_deploy'),
    ('wait_testbed_schedule', 'saved')
]


def is_valid_transition(experiment: AerpawExperiment, next_state: str, user: AerpawUser) -> bool:
    transition = (experiment.state(), next_state)
    if experiment.state() == next_state:
        # TODO: placeholder for same state update options
        pass
    if user.is_operator() and (experiment.is_creator(user) or experiment.is_member(user)):
        return (transition in _VALID_OPERATOR_TRANSITION) or (transition in _VALID_EXPERIMENTER_TRANSITION)
    elif experiment.is_creator(user) or experiment.is_member(user):
        return transition in _VALID_EXPERIMENTER_TRANSITION
    elif user.is_operator():
        return transition in _VALID_OPERATOR_TRANSITION
    else:
        return False


def transition_experiment_state(request, experiment: AerpawExperiment, next_state: str = None):
    """
    Transition experiment state with actions
    - ACTIVE_DEVELOPMENT --> SAVING_DEVELOPMENT - save development session
    - ACTIVE_EMULATION --> SAVED - emulation complete - Flags 100 or 101
    - ACTIVE_SANDBOX --> SAVING_SANDBOX - save sandbox session
    - ACTIVE_TESTBED --> SAVED - execution complete - Flags 010
    - SAVING_DEVELOPMENT --> SAVED - move to saved state - Flags 000
    - SAVING_DEVELOPMENT --> ACTIVE_DEVELOPMENT - resume development session
    - SAVING_SANDBOX --> SAVED - move to saved state - Flags 000
    - SAVING_SANDBOX --> ACTIVE_SANDBOX - resume sandbox session
    - SAVED --> WAIT_DEVELOPMENT_DEPLOY - start development session
    - SAVED --> WAIT_SANDBOX_DEPLOY - schedule sandbox session
    - SAVED --> WAIT_EMULATION_SCHEDULE - reqeust emulation session
    - SAVED --> WAIT_TESTBED_SCHEDULE - request testbed session (allowed if (E&&P)|T
    - WAIT_DEVELOPMENT_DEPLOY --> ACTIVE_DEVELOPMENT - deployment on development VMs complete
    - WAIT_DEVELOPMENT_DEPLOY --> SAVED - failure to deploy
    - WAIT_EMULATION_DEPLOY --> ACTIVE_EMULATION - scheduled deployment of emulation complete
    - WAIT_EMULATION_DEPLOY --> SAVED - cancel
    - WAIT_EMULATION_SCHEDULE --> WAIT_EMULATION_DEPLOY - schedule
    - WAIT_EMULATION_SCHEDULE --> SAVED - cancel pending emulation session
    - WAIT_SANDBOX_DEPLOY --> ACTIVE_SANDBOX - scheduled deployment on sandbox complete
    - WAIT_SANDBOX_DEPLOY --> SAVED - cancel pending sandbox session
    - WAIT_TESTBED_DEPLOY --> ACTIVE_TESTBED - scheduled deployment of testbed complete
    - WAIT_TESTBED_DEPLOY --> SAVED - cancel
    - WAIT_TESTBED_SCHEDULE --> WAIT_TESTBED_DEPLOY - schedule
    - WAIT_TESTBED_SCHEDULE --> SAVED - cancel pending testbed session
    - SAME_STATE --> SAME_STATE - non-transition option for ???
    """
    transition = (experiment.state(), next_state)
    # ACTIVE_DEVELOPMENT --> SAVING_DEVELOPMENT - save development session
    if transition == ('active_development', 'saving_development'):
        active_development_to_saving_development(request=request, experiment=experiment)
    # ACTIVE_SANDBOX --> SAVING_SANDBOX - save sandbox session
    elif transition == ('active_sandbox', 'saving_sandbox'):
        active_sandbox_to_saving_sandbox(request=request, experiment=experiment)
    # SAVING_DEVELOPMENT --> SAVED - move to saved state
    # Flags 000
    elif transition == ('saving_development', 'saved'):
        saving_development_to_saved(request=request, experiment=experiment)
    # SAVING_DEVELOPMENT --> ACTIV_DEVELOPMENT - resume development session
    elif transition == ('saving_development', 'active_development'):
        saving_development_to_active_development(request=request, experiment=experiment)
    # SAVING_SANDBOX --> SAVED - move to saved state
    # Flags 000
    elif transition == ('saving_sandbox', 'saved'):
        saving_sandbox_to_saved(request=request, experiment=experiment)
    # SAVING_SANDBOX --> ACTIVE_SANDBOX - resume sandbox session
    elif transition == ('save_sandbox', 'wait_sandbox_deploy'):
        saving_sandbox_to_active_sandbox(request=request, experiment=experiment)
    # ACTIVE_EMULATION --> SAVED - emulation complete
    # Flags 100 or 101
    elif transition == ('active_emulation', 'saved'):
        active_emulation_to_saved(request=request, experiment=experiment)
    # ACTIVE_TESTBED --> SAVED - execution complete
    # Flags 010
    elif transition == ('active_testbed', 'saved'):
        active_testbed_to_saved(request=request, experiment=experiment)
    # SAVED --> WAIT_DEVELOPMENT_DEPLOY - start development session
    elif transition == ('saved', 'wait_development_deploy'):
        saved_to_wait_development_deploy(request=request, experiment=experiment)
    # SAVED --> WAIT_SANDBOX_DEPLOY - schedule sandbox session
    elif transition == ('saved', 'wait_sandbox_deploy'):
        saved_to_wait_sandbox_deploy(request=request, experiment=experiment)
    # SAVED --> WAIT_EMULATION_SCHEDULE - reqeust emulation session
    elif transition == ('saved', 'wait_emulation_schedule'):
        saved_to_wait_emulation_schedule(request=request, experiment=experiment)
    # SAVED --> WAIT_TESTBED_SCHEDULE - request testbed session (allowed if (E&&P)|T
    elif transition == ('saved', 'wait_testbed_schedule'):
        saved_to_wait_testbed_schedule(request=request, experiment=experiment)
    # WAIT_DEVELOPMENT_DEPLOY --> ACTIVE_DEVELOPMENT - deployment on development VMs complete
    elif transition == ('wait_development_deploy', 'active_development'):
        wait_development_deploy_to_active_development(request=request, experiment=experiment)
    # WAIT_DEVELOPMENT_DEPLOY --> SAVED - failure to deploy
    elif transition == ('wait_development_deploy', 'saved'):
        wait_development_deploy_to_saved(request=request, experiment=experiment)
    # WAIT_EMULATION_DEPLOY --> ACTIVE_EMULATION - scheduled deployment of emulation complete
    elif transition == ('wait_emulation_deploy', 'active_emulation'):
        wait_emulation_deploy_to_active_emulation(request=request, experiment=experiment)
    # WAIT_DEVELOPMENT_DEPLOY --> SAVED - failure to deploy
    elif transition == ('wait_emulation_deploy', 'saved'):
        wait_emulation_deploy_to_saved(request=request, experiment=experiment)
    # WAIT_EMULATION_SCHEDULE --> WAIT_EMULATION_DEPLOY - schedule
    elif transition == ('wait_emulation_schedule', 'wait_emulation_deploy'):
        wait_emulation_schedule_to_wait_emulation_deploy(request=request, experiment=experiment)
    # WAIT_EMULATION_SCHEDULE --> SAVED - cancel pending emulation session
    elif transition == ('wait_emulation_schedule', 'saved'):
        wait_emulation_schedule_to_saved(request=request, experiment=experiment)
    # WAIT_SANDBOX_DEPLOY --> ACTIVE_SANDBOX - scheduled deployment on sandbox complete
    elif transition == ('wait_sandbox_deploy', 'active_sandbox'):
        wait_sandbox_deploy_to_active_sandbox(request=request, experiment=experiment)
    # WAIT_SANDBOX_DEPLOY --> SAVED - cancel pending sandbox session
    elif transition == ('wait_sandbox_deploy', 'saved'):
        wait_sandbox_deploy_to_saved(request=request, experiment=experiment)
    # WAIT_TESTBED_DEPLOY --> ACTIVE_TESTBED - scheduled deployment of testbed complete
    elif transition == ('wait_testbed_deploy', 'active_testbed'):
        wait_testbed_deploy_to_active_testbed(request=request, experiment=experiment)
    # WAIT_TESTBED_DEPLOY --> SAVED - cancel
    elif transition == ('wait_testbed_deploy', 'saved'):
        wait_testbed_deploy_to_saved(request=request, experiment=experiment)
    # WAIT_TESTBED_SCHEDULE --> WAIT_TESTBED_DEPLOY - schedule
    elif transition == ('wait_testbed_schedule', 'wait_testbed_deploy'):
        wait_testbed_schedule_to_wait_testbed_deploy(request=request, experiment=experiment)
    # WAIT_TESTBED_SCHEDULE --> SAVED - cancel pending testbed session
    elif transition == ('wait_testbed_schedule', 'saved'):
        wait_testbed_schedule_to_saved(request=request, experiment=experiment)
    # Placeholder for same state update options
    else:
        # TODO: placeholder for same state update options
        same_to_same(request=request, experiment=experiment)

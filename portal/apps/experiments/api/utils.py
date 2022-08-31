from portal.apps.experiments.models import AerpawExperiment

"""
Valid experiment transition states
- ref: https://user-images.githubusercontent.com/5332509/186757199-86f44e94-e590-4e1d-9763-5f8401c69b5d.png
"""
_VALID_EXP_TRANSITION = [
    ('active_development', 'saved'),
    ('active_emulation', 'saved'),
    ('active_sandbox', 'saved'),
    ('active_testbed', 'saved'),
    ('saved', 'wait_development_deploy'),
    ('saved', 'wait_sandbox_deploy'),
    ('saved', 'wait_emulation_schedule'),
    ('saved', 'wait_testbed_schedule'),
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

_OPERATOR_ONLY_TRANSITION = [
    ('active_emulation', 'saved'),
    ('active_testbed', 'saved'),
    ('wait_development_deploy', 'active_development'),
    ('wait_development_deploy', 'saved'),
    ('wait_emulation_deploy', 'active_emulation'),
    ('wait_emulation_schedule', 'wait_emulation_deploy'),
    ('wait_sandbox_deploy', 'active_sandbox'),
    ('wait_testbed_deploy', 'active_testbed'),
    ('wait_testbed_schedule', 'wait_testbed_deploy')
]


def is_valid_transition(experiment: AerpawExperiment, next_state: str = None) -> bool:
    transition = (experiment.state(), next_state)
    if experiment.state() == next_state:
        # TODO: placeholder for same state update options
        return True
    return transition in _VALID_EXP_TRANSITION


def operator_only_transition(experiment: AerpawExperiment, next_state: str = None) -> bool:
    transition = (experiment.state(), next_state)
    if experiment.state() == next_state:
        # TODO: placeholder for same state update options
        return True
    return transition in _VALID_EXP_TRANSITION


def transition_experiment_state(request, experiment: AerpawExperiment, next_state: str = None):
    transition = (experiment.state(), next_state)
    emulation_passed = False
    if request:
        try:
            print(request.data)
            emulation_passed = request.data.get('emulation_passed', False)
        except Exception as exc:
            print(exc)
    # ACTIVE_DEVELOPMENT --> SAVED - save development session
    # Flags 000 (e.g. experimenter logged out of all VMs for one hour)
    if transition == ('active_development', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.experiment_flags = '000'
        experiment.save()
    # ACTIVE_EMULATION --> SAVED - emulation complete
    # Flags 100 or 101
    elif transition == ('active_emulation', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        if emulation_passed:
            experiment.experiment_flags = '101'
        else:
            experiment.experiment_flags = '100'
        experiment.save()
    # ACTIVE_SANDBOX --> SAVED - save sandbox session
    # Flags 000 (e.g. end of scheduled sandbox session)
    elif transition == ('active_sandbox', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.experiment_flags = '000'
        experiment.save()
    # ACTIVE_TESTBED --> SAVED - execution complete
    # Flags 010
    elif transition == ('active_testbed', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.experiment_flags = '010'
        experiment.save()
    # SAVED --> WAIT_DEVELOPMENT_DEPLOY - start development session
    elif transition == ('saved', 'wait_development_deploy'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY
        experiment.experiment_flags = '000'
        experiment.save()
    # SAVED --> WAIT_SANDBOX_DEPLOY - schedule sandbox session
    elif transition == ('saved', 'wait_sandbox_deploy'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY
        experiment.experiment_flags = '000'
        experiment.save()
    # SAVED --> WAIT_EMULATION_SCHEDULE - reqeust emulation session
    elif transition == ('saved', 'wait_emulation_schedule'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE
        experiment.experiment_flags = '000'
        experiment.save()
    # SAVED --> WAIT_TESTBED_SCHEDULE - request testbed session (allowed if (E&&P)|T
    elif transition == ('saved', 'wait_testbed_schedule'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE
        experiment.experiment_flags = '000'
        experiment.save()
    # WAIT_DEVELOPMENT_DEPLOY --> ACTIVE_DEVELOPMENT - deployment on development VMs complete
    elif transition == ('wait_development_deploy', 'active_development'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_DEVELOPMENT
        experiment.save()
    # WAIT_DEVELOPMENT_DEPLOY --> SAVED - failure to deploy
    elif transition == ('wait_development_deploy', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.save()
    # WAIT_EMULATION_DEPLOY --> ACTIVE_EMULATION - scheduled deployment of emulation complete
    elif transition == ('wait_emulation_deploy', 'active_emulation'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_EMULATION
        experiment.save()
    # WAIT_DEVELOPMENT_DEPLOY --> SAVED - failure to deploy
    elif transition == ('wait_emulation_deploy', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.save()
    # WAIT_EMULATION_SCHEDULE --> WAIT_EMULATION_DEPLOY - schedule
    elif transition == ('wait_emulation_schedule', 'wait_emulation_deploy'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_DEPLOY
        experiment.save()
    # WAIT_EMULATION_SCHEDULE --> SAVED - cancel pending emulation session
    elif transition == ('wait_emulation_schedule', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.save()
    # WAIT_SANDBOX_DEPLOY --> ACTIVE_SANDBOX - scheduled deployment on sandbox complete
    elif transition == ('wait_sandbox_deploy', 'active_sandbox'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_SANDBOX
        experiment.save()
    # WAIT_SANDBOX_DEPLOY --> SAVED - cancel pending sandbox session
    elif transition == ('wait_sandbox_deploy', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.save()
    # WAIT_TESTBED_DEPLOY --> ACTIVE_TESTBED - scheduled deployment of testbed complete
    elif transition == ('wait_testbed_deploy', 'active_testbed'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_TESTBED
        experiment.save()
    # WAIT_TESTBED_DEPLOY --> SAVED - cancel
    elif transition == ('wait_testbed_deploy', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.save()
    # WAIT_TESTBED_SCHEDULE --> WAIT_TESTBED_DEPLOY - schedule
    elif transition == ('wait_testbed_schedule', 'wait_testbed_deploy'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_DEPLOY
        experiment.save()
    # WAIT_TESTBED_SCHEDULE --> SAVED - cancel pending testbed session
    elif transition == ('wait_testbed_schedule', 'saved'):
        experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
        experiment.save()
    # Placeholder for same state update options
    else:
        # TODO: placeholder for same state update options
        pass

from portal.apps.experiments.models import AerpawExperiment


def active_development_to_saved(request, experiment: AerpawExperiment):
    """
    ACTIVE_DEVELOPMENT --> SAVED
    - save development session
    - Flags 000 (e.g. experimenter logged out of all VMs for one hour)

    Permissions:
    - experimenter OR
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '000'
    experiment.save()


def active_emulation_to_saved(request, experiment: AerpawExperiment):
    """
    ACTIVE_EMULATION --> SAVED
    - emulation complete
    - Flags 100 or 101

    Permissions:
    - operator
    """
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

    Permissions:
    - experimenter OR
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '000'
    experiment.save()


def active_testbed_to_saved(request, experiment: AerpawExperiment):
    """
    ACTIVE_TESTBED --> SAVED
    - execution complete
    - Flags 010

    Permissions:
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.experiment_flags = '010'
    experiment.save()


def saved_to_wait_development_deploy(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_DEVELOPMENT_DEPLOY
    - start development session

    Permissions:
    - experimenter
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY
    experiment.save()


def saved_to_wait_sandbox_deploy(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_SANDBOX_DEPLOY
    - schedule sandbox session

    Permissions:
    - experimenter
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY
    experiment.save()


def saved_to_wait_emulation_schedule(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_EMULATION_SCHEDULE
    - reqeust emulation session

    Permissions:
    - experimenter
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE
    experiment.save()


def saved_to_wait_testbed_schedule(request, experiment: AerpawExperiment):
    """
    SAVED --> WAIT_TESTBED_SCHEDULE
    - request testbed session (allowed if (E&&P)|T

    Permissions:
    - experimenter
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE
    experiment.save()


def wait_development_deploy_to_active_development(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> ACTIVE_DEVELOPMENT
    - deployment on development VMs complete

    Permissions:
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_DEVELOPMENT
    experiment.experiment_flags = '000'
    experiment.save()


def wait_development_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> SAVED
    - failure to deploy

    Permissions:
    - experimenter OR
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_emulation_deploy_to_active_emulation(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_DEPLOY --> ACTIVE_EMULATION
    - scheduled deployment of emulation complete

    Permissions:
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_EMULATION
    experiment.save()


def wait_emulation_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_DEVELOPMENT_DEPLOY --> SAVED
    - failure to deploy

    Permissions:
    - experimenter OR
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_emulation_schedule_to_wait_emulation_deploy(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_SCHEDULE --> WAIT_EMULATION_DEPLOY
    - schedule

    Permissions:
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_EMULATION_DEPLOY
    experiment.save()


def wait_emulation_schedule_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_EMULATION_SCHEDULE --> SAVED
    - cancel pending emulation session

    Permissions:
    - experimenter OR
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_sandbox_deploy_to_active_sandbox(request, experiment: AerpawExperiment):
    """
    WAIT_SANDBOX_DEPLOY --> ACTIVE_SANDBOX
    - scheduled deployment on sandbox complete

    Permissions:
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_SANDBOX
    experiment.experiment_flags = '000'
    experiment.save()


def wait_sandbox_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_SANDBOX_DEPLOY --> SAVED
    - cancel pending sandbox session

    Permissions:
    - experimenter OR
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_testbed_deploy_to_active_testbed(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_DEPLOY --> ACTIVE_TESTBED
    - scheduled deployment of testbed complete

    Permissions:
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.ACTIVE_TESTBED
    experiment.save()


def wait_testbed_deploy_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_DEPLOY --> SAVED
    - cancel

    Permissions:
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.SAVED
    experiment.save()


def wait_testbed_schedule_to_wait_testbed_deploy(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_SCHEDULE --> WAIT_TESTBED_DEPLOY
    - schedule

    Permissions:
    - operator
    """
    experiment.experiment_state = AerpawExperiment.ExperimentState.WAIT_TESTBED_DEPLOY
    experiment.save()


def wait_testbed_schedule_to_saved(request, experiment: AerpawExperiment):
    """
    WAIT_TESTBED_SCHEDULE --> SAVED
    - cancel pending testbed session

    Permissions:
    - experimenter OR
    - operator
    """
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

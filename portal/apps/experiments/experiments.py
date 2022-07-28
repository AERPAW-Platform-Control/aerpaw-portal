import json
import logging
import os
import time
import uuid
from datetime import datetime

from django.utils import timezone

from portal.apps.operations.models import CanonicalNumber
from portal.apps.projects.models import AerpawProject
from portal.apps.resources.models import AerpawResource
from portal.apps.users.models import AerpawUser
from .models import AerpawExperiment

logger = logging.getLogger(__name__)


def send_request_to_testbed(request, experiment):
    action = None
    if experiment.state == AerpawExperiment.STATE_DEPLOYING:
        action = 'START'
    elif experiment.state == AerpawExperiment.STATE_IDLE:
        action = 'SAVE and EXIT'
    elif experiment.state == AerpawExperiment.STATE_SUBMIT:
        action = 'SUBMIT'

    if action:
        subject = 'Aerpaw Experiment Action Session Request: {} {}:{}'.format(action,
                                                                              str(experiment.uuid),
                                                                              experiment.stage)
        message = "[{}]\n\n".format(subject) \
                  + "Experiment Name: {}\n".format(str(experiment)) \
                  + "Project: {}\n".format(experiment.project) \
                  + "User: {}\n\n".format(request.user.username)
        if action == 'SUBMIT':
            message += "Testbed Experiment Description: {}\n\n".format(experiment.submit_notes)
        if action == 'START' or action == 'SUBMIT':
            try:
                session_req = generate_experiment_session_request(request, experiment)
                session_req_json=json.dumps(session_req) #dict to json str
            except TypeError:
                session_req_json=json.dumps({"experiment_resource_definition":"Unable to serialize the object"})
            message += "Experiment {} Session Request:\n{}\n".format(experiment.stage, session_req_json)

        receivers = []
        operators = list(AerpawUser.objects.filter(groups__name='operator'))
        for operator in operators:
            receivers.append(operator)
        logger.warning("send_email:\n" + subject)
        logger.warning(message)
        #portal_mail(subject=subject, body_message=message, sender=request.user,
        #            receivers=receivers,
        #            reference_note=None, reference_url=None)
        if action == 'START':
            kwargs = {'experiment_name': str(experiment)}
            #ack_mail(
            #    template='experiment_init', user_name=request.user.display_name,
            #    user_email=request.user.email, **kwargs
            #


def experiment_state_change(request, experiment, backend_status):
    automated = False

    logger.warning(
        '[{}] current state={}, backend_status={}'.format(experiment.name, experiment.state,
                                                          backend_status))

    if backend_status == 'unknown':
        return

    elif backend_status == 'not_started' or backend_status == 'terminating':
        # the emulab is not doing anything or soon be idle
        if experiment.state != AerpawExperiment.STATE_SAVED:
            if experiment.can_snapshot():
                experiment.is_snapshotted = True
            experiment.idle()
            experiment.save()
            send_request_to_testbed(request, experiment)
        return

    elif backend_status != 'ready':
        # possible status: created, provisioning, provisioned ...
        # the emulab is provisioning the node or booting
        if experiment.state < AerpawExperiment.STATE_WAIT_DEVELOPMENT_DEPLOY:
            experiment.provision()
            experiment.save()
        return

    elif backend_status == 'ready':
        if experiment.state < AerpawExperiment.STATE_WAIT_DEVELOPMENT_DEPLOY:
            prev_state = experiment.state
            experiment.deploy()  # change state first so get_emulab_manifest can function properly
            experiment.save()


            manifest = generate_experiment_session_request(request, experiment)

            if manifest != None:
                send_request_to_testbed(request, experiment)
                # since new run is started, reset is_snapshotted flag and message
                experiment.is_snapshotted = False
                experiment.message = ""
                experiment.save()
            else:
                logger.error('!! Error - Manifest is not available')
                experiment.state = prev_state  # revert state
                experiment.save()
                return

            if automated:
                # Call some provisioning backend system, Place Holder
                hostname = manifest['nodes'][0]['hostname']
                logger.warning('[{}] deployment host: {}'.format(experiment.name, hostname))
            return


def generate_experiment_session_request(request, experiment):
    """
    Generate experiment session request from resource definition and database or emulab resource
    This should be rewritten and update via some defined openapi

    :param request:
    :param experiment:
    """
    session_req = {}
    if experiment.stage != "Idle":
        session_req['ap_msg_type'] = 'experiment_{}_session_request'.format(
            experiment.stage).lower()

    resources = experiment.resources
    if resources is None:
        return None
    resource_def = {'experiment_uuid': str(experiment.uuid), 'experiment_idx': experiment.id,
                    'nodes': resources}
    session_req['experiment_resource_definition'] = resource_def

    user = {'username': experiment.created_by.username.split('@')[0],
            'publickey': experiment.created_by.publickey}
    session_req['user'] = user

    return session_req

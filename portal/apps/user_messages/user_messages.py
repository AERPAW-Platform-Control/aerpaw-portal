import os
from datetime import datetime, timezone
from uuid import uuid4

from django.core.mail import send_mail

from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.projects.models import AerpawProject
from portal.apps.user_messages.models import AerpawUserMessage
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.users.models import AerpawRolesEnum, AerpawUser

annotation = """
***************************************************************************************
***** ATTENTION - an email has been sent to the user as denoted below - ATTENTION *****
***************************************************************************************
"""


def send_portal_mail_from_message(request, *args, **kwargs) -> bool:
    """
    Derive mail parameters from UserMessages **kwargs
    - message_body     - string
    - message_owner    - int:user_id
    - message_subject  - string
    - received_by      - array of int:user_id

    send_mail(subject, message, from_email, recipient_list)
    """
    try:
        subject = kwargs.get('message_subject')
        message = kwargs.get('message_body')
        from_email = os.getenv('EMAIL_HOST_USER')
        recipient_list = [u.email for u in AerpawUser.objects.filter(id__in=kwargs.get('received_by')).all()]
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as exc:
        print(exc)
        new_error(exc, request.user)
        return False


def user_message_create(request, *args, **kwargs) -> bool:
    """
    UserMessages **kwargs
    - message_body     - string
    - message_owner    - int:user_id
    - message_subject  - string
    - received_by      - array of int:user_id
    """
    try:
        user = AerpawUser.objects.filter(id=request.user.id).first()
        received_by = AerpawUser.objects.filter(id__in=kwargs.get('received_by')).all()
        # create user message
        user_message = AerpawUserMessage()
        user_message.created = datetime.now(timezone.utc)
        user_message.created_by = user.username
        user_message.message_body = kwargs.get('message_body', None)
        user_message.message_owner = AerpawUser.objects.filter(id=kwargs.get('message_owner')).first()
        user_message.message_subject = kwargs.get('message_subject', None)
        user_message.modified = datetime.now(timezone.utc)
        user_message.modified_by = user.username
        user_message.sent_by = user
        user_message.uuid = uuid4()
        user_message.save()
        # add received by to existing user message
        for u in received_by:
            user_message.received_by.add(u)
        user_message.save()
        return True
    except Exception as exc:
        print(exc)
        new_error(exc, request.user)
        return False






def generate_user_messages_from_user_request(request, user_request: dict):
    """
    Example UserRequest - project join request
    {
        'completed_by': None,
        'completed_date': None,
        'is_approved': None,
        'last_modified_by': 4,
        'modified_date': '2022-10-21T10:06:08.576584-04:00',
        'received_by': [1, 3],
        'request_id': 4,
        'request_note': '[example code project] - project join request',
        'request_type': 'project',
        'request_type_id': 3,
        'requested_by': 4,
        'requested_date': '2022-10-21T10:06:08.563034-04:00',
        'response_date': None,
        'response_note': None
    }

    UserMessage - required components (per message)
    - message_body     - string
    - message_owner    - int:user_id
    - message_subject  - string
    - received_by      - array of int:user_id
    """
    received_by = user_request.get('received_by')
    message_owner_ids = received_by.copy()
    message_owner_ids.append(user_request.get('requested_by'))
    request_type = user_request.get('request_type')
    user_display_name = AerpawUser.objects.filter(id=user_request.get('requested_by')).first().display_name
    if not user_request.get('response_date'):
        message_subject = 'REQUEST: ' + user_request.get('request_note')
    else:
        message_subject = 'RESPONSE: ' + user_request.get('request_note')
        received_by.append(user_request.get('requested_by'))
        received_by.remove(request.user.id)
    message_body = """
request_type: {0}

requested_by: {1}

request_note: {2}
requested_date: {3}

received_by: {4}

completed_by: {5}
is_approved: {6}
response_note: {7}
response_date: {8}
""".format(
        request_type,
        user_display_name,
        user_request.get('request_note'),
        datetime.strptime(user_request.get('requested_date'), "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%m/%d/%Y, %H:%M:%S"),
        [u.display_name for u in AerpawUser.objects.filter(id__in=received_by).all()],
        AerpawUser.objects.filter(id=user_request.get('completed_by')).first().display_name if user_request.get(
            'completed_by') else '-----',
        user_request.get('is_approved') if str(user_request.get('is_approved')).casefold() in ['true',
                                                                                               'false'] else '-----',
        user_request.get('response_note') if user_request.get('response_note') else '-----',
        datetime.strptime(user_request.get('response_date'), "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
            "%m/%d/%Y, %H:%M:%S") if user_request.get('response_date') else '-----'
    )
    for owner in message_owner_ids:
        kwargs = {
            'message_body': message_body,
            'message_owner': owner,
            'message_subject': message_subject,
            'received_by': received_by
        }
        user_message_create(request=request, **kwargs)
    # emails
    if request_type == AerpawUserRequest.RequestType.ROLE.value:
        # role
        if not user_request.get('response_date'):
            # role request
            if user_request.get('request_note') == '[{0}] - role request'.format(AerpawRolesEnum.EXPERIMENTER.value):
                # experimenter role
                message_subject = '[AERPAW] Request for Experimenter role: {0}'.format(user_display_name)
                message_body = """
Hi {0},

Your request to be granted the role of Experimenter has been forwarded to AERPAW Ops.
You will receive another email when your request has been addressed.
As noted in the AERPAW User Manual, this can take a variable amount of time, from minutes to hours.
""".format(user_display_name)
            elif user_request.get('request_note') == '[{0}] - role request'.format(AerpawRolesEnum.PI.value):
                # pi role
                message_subject = '[AERPAW] Request for PI role: {0}'.format(user_display_name)
                message_body = """
Hi {0},

Your request to be granted the role of Principal Investigator has been forwarded to AERPAW Ops.
You will receive another email when your request has been addressed.
As noted in the AERPAW User Manual, this can take a variable amount of time, from minutes to hours.
""".format(user_display_name)
        else:
            # role response
            if user_request.get('request_note') == '[{0}] - role request'.format(AerpawRolesEnum.EXPERIMENTER.value):
                # experimenter role
                message_subject = '[AERPAW] re: Request for Experimenter role: {0}'.format(user_display_name)
                message_body = """
Hi {0},

Your request to be granted the role of Experimenter has been {1}.

Note: {2}
""".format(user_display_name,
           'Approved' if str(user_request.get('is_approved')).casefold() in ['true'] else 'Denied',
           user_request.get('response_note'))
            elif user_request.get('request_note') == '[{0}] - role request'.format(AerpawRolesEnum.PI.value):
                # pi role
                message_subject = '[AERPAW] re: Request for PI role: {0}'.format(user_display_name)
                message_body = """
Hi {0},

Your request to be granted the role of Principal Investigator has been {1}.

Note: {2}
""".format(user_display_name,
           'Approved' if str(user_request.get('is_approved')).casefold() in ['true'] else 'Denied',
           user_request.get('response_note'))
    elif request_type == AerpawUserRequest.RequestType.PROJECT.value:
        # project
        project_name = AerpawProject.objects.get(pk=user_request.get('request_type_id')).name
        if not user_request.get('response_date'):
            # project request
            message_subject = '[AERPAW] Request to join Project: {0}'.format(project_name)
            message_body = """
Hi {0},

Your request to join the Project: {1} has been forwarded to the owners of this project.
You will receive an email confirmation once one of the Project Owners has approved/denied this request.
""".format(user_display_name, project_name)
        else:
            # project response
            message_subject = '[AERPAW] re: Request to join Project: {0}'.format(project_name)
            message_body = """
Hi {0},

Your request to join the Project: {1} has been {2}.

Note: {3}
""".format(user_display_name,
           project_name,
           'Approved' if str(user_request.get('is_approved')).casefold() in ['true'] else 'Denied',
           user_request.get('response_note'))
    elif request_type == AerpawUserRequest.RequestType.EXPERIMENT.value:
        # experiment
        experiment_name = AerpawExperiment.objects.get(pk=user_request.get('request_type_id')).name
        if not user_request.get('response_date'):
            # experiment request
            message_subject = '[AERPAW] Request to join Experiment: {0}'.format(experiment_name)
            message_body = """
Hi {0},

Your request to join the Experiment: {1} has been forwarded to the members of this experiment.
You will receive an email confirmation once one of the Experiment Members has approved/denied this request.
""".format(user_display_name, experiment_name)
        else:
            # experiment response
            message_subject = '[AERPAW] re: Request to join Experiment: {0}'.format(experiment_name)
            message_body = """
Hi {0},

Your request to join the Experiment: {1} has been {2}.

Note: {3}
""".format(user_display_name,
           experiment_name,
           'Approved' if str(user_request.get('is_approved')).casefold() in ['true'] else 'Denied',
           user_request.get('response_note'))
    else:
        message_owner_ids = []
    # set annotated message body
    annotated_message_body = annotation + message_body
    for owner in message_owner_ids:
        if owner != user_request.get('requested_by'):
            email_message_body = annotated_message_body
        else:
            email_message_body = message_body
        kwargs = {
            'message_body': email_message_body,
            'message_owner': request.user.id,
            'message_subject': message_subject,
            'received_by': [owner]
        }
        send_portal_mail_from_message(request=request, **kwargs)


def generate_new_user_welcome_message(request, user: AerpawUser):
    message_subject = '[AERPAW] Welcome {0} to the AERPAW portal!'.format(user.display_name)
    message_body = """
Hi {0},

Welcome to the AERPAW Portal
        
User manuals, tutorials, and other relevant documentation can be found at the following links; 
please refer to relevant instructions before attempting to use this Portal.

- AERPAW Main Site: https://aerpaw.org/
- AERPAW User Manual: https://sites.google.com/ncsu.edu/aerpaw-wiki/
- AERPAW Acceptable Use Policy: https://sites.google.com/ncsu.edu/aerpaw-wiki/aerpaw-user-manual/2-experiment-lifecycle-workflows/2-5-acceptable-use-policy-aup

Thank you for joining AERPAW,
- AERPAW Ops
""".format(user.display_name)
    kwargs = {
        'message_body': message_body,
        'message_owner': user.id,
        'message_subject': message_subject,
        'received_by': [user.id]
    }
    request.user = user
    # create portal message
    user_message_create(request=request, **kwargs)
    # send welcome email
    send_portal_mail_from_message(request=request, **kwargs)


def generate_user_messages_from_project_membership(request, project: AerpawProject, project_members: [int],
                                                   membership_type: str, add: bool = False):
    """
    UserMessage - required components (per message)
    - message_body     - string
    - message_owner    - int:user_id
    - message_subject  - string
    - received_by      - array of int:user_id
    """
    project_owner_ids = [o.id for o in project.project_owners().all()]
    project_owner_ids.append(AerpawUser.objects.get(username=project.created_by).id)
    project_owner_ids = list(set(project_owner_ids))
    for member in project_members:
        user_display_name = AerpawUser.objects.filter(id=member).first().display_name
        if add:
            message_subject = '[AERPAW] {0} added to Project: {1} as {2}'.format(user_display_name, project.name,
                                                                                 membership_type)
            message_body = """
Hi {0},

You have been added to Project: {1} as {2}
""".format(user_display_name, project.name, membership_type)
        else:
            message_subject = '[AERPAW] {0} removed from Project: {1} as {2}'.format(user_display_name, project.name,
                                                                                     membership_type)
            message_body = """
Hi {0},

You have been removed from Project: {1} as {2}
""".format(user_display_name, project.name, membership_type)
        received_by_all = project_owner_ids.copy()
        received_by_all.append(member)
        received_by = set(received_by_all)
        for r in received_by:
            kwargs = {
                'message_body': message_body,
                'message_owner': r,
                'message_subject': message_subject,
                'received_by': received_by
            }
            user_message_create(request=request, **kwargs)
        # set annotated message body
        annotated_message_body = annotation + message_body
        # send email
        for p in received_by:
            if p not in project_members:
                email_message_body = annotated_message_body
            else:
                email_message_body = message_body
            kwargs = {
                'message_body': email_message_body,
                'message_subject': message_subject,
                'received_by': [p]
            }
            send_portal_mail_from_message(request=request, **kwargs)


def generate_user_messages_from_experiment_membership(request, experiment: AerpawExperiment, experiment_members: [int],
                                                      add: bool = False):
    """
    UserMessage - required components (per message)
    - message_body     - string
    - message_owner    - int:user_id
    - message_subject  - string
    - received_by      - array of int:user_id
    """
    experiment_member_ids = [m.id for m in experiment.experiment_members().all()]
    experiment_member_ids.append(AerpawUser.objects.get(username=experiment.created_by).id)
    experiment_member_ids = list(set(experiment_member_ids))
    for member in experiment_members:
        user_display_name = AerpawUser.objects.filter(id=member).first().display_name
        if add:
            message_subject = '[AERPAW] {0} added to Experiment: {1} as Member'.format(user_display_name,
                                                                                       experiment.name)
            message_body = """
Hi {0},

You have been added to Experiment: {1} as Member
""".format(user_display_name, experiment.name)
        else:
            message_subject = '[AERPAW] {0} removed from Experiment: {1} as Member'.format(user_display_name,
                                                                                           experiment.name)
            message_body = """
Hi {0},

You have been removed from Experiment: {1} as Member
""".format(user_display_name, experiment.name)
        received_by_all = experiment_member_ids.copy()
        received_by_all.append(member)
        received_by = set(received_by_all)
        for r in received_by:
            kwargs = {
                'message_body': message_body,
                'message_owner': r,
                'message_subject': message_subject,
                'received_by': received_by
            }
            user_message_create(request=request, **kwargs)
        # set annotated message body
        annotated_message_body = annotation + message_body
        # send email
        for p in received_by:
            if p not in experiment_members:
                email_message_body = annotated_message_body
            else:
                email_message_body = message_body
            kwargs = {
                'message_body': email_message_body,
                'message_subject': message_subject,
                'received_by': [p]
            }
            send_portal_mail_from_message(request=request, **kwargs)


def generate_user_messages_for_development(request, experiment: AerpawExperiment):
    """
    UserMessage - required components (per message)
    - message_body     - string
    - message_owner    - int:user_id
    - message_subject  - string
    - received_by      - array of int:user_id
    """
    received_by_all = [m.id for m in experiment.experiment_members().all()]
    received_by_all.append(AerpawUser.objects.get(username=experiment.created_by).id)
    if experiment.state() == AerpawExperiment.ExperimentState.WAIT_DEVELOPMENT_DEPLOY.value:
        # Initiate Development - button pressed by user
        # - notify: experiment_members
        message_subject = '[AERPAW] Request to initiate development session for Experiment: {0}'.format(experiment.name)
        message_body = """
Your request to initiate a development session for the experiment: {0} has been forwarded to AERPAW Ops.
When the Development Session is ready for you, you will receive another email with access info.
As noted in the AERPAW User Manual, this can take a variable amount of time, from minutes to hours.
""".format(experiment.name)
    elif experiment.state() == AerpawExperiment.ExperimentState.ACTIVE_DEVELOPMENT.value:
        # Development environment is ready for use
        # - notify: experiment_members
        message_subject = '[AERPAW] Development session for Experiment: {0} is active'.format(experiment.name)
        message_body = """
Your development session for the experiment: {0} is ready for use.
""".format(experiment.name)
    elif experiment.state() == AerpawExperiment.ExperimentState.SAVING_DEVELOPMENT.value:
        # Saving Development Environment
        # - notify: experiment_members
        message_subject = '[AERPAW] Saving development environment for Experiment: {0}'.format(experiment.name)
        message_body = """
Saving experiment: {0}
As noted in the AERPAW User Manual, this can take a variable amount of time, from minutes to hours.
""".format(experiment.name)
    elif experiment.state() == AerpawExperiment.ExperimentState.SAVED.value:
        # Development session has ended and moved back to saved state
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Development session for Experiment: {0} has been ended'.format(experiment.name)
        message_body = """
Development session for Experiment: {0} has been ended and the experiment saved.
""".format(experiment.name)
    else:
        message_subject = '[AERPAW] Invalid state for Experiment: {0}'.format(experiment.name)
        message_body = """
Experiment: {0} is in an Invalid state
""".format(experiment.name)
    # send message
    received_by = set(received_by_all)
    for member in received_by:
        kwargs = {
            'message_body': message_body,
            'message_owner': member,
            'message_subject': message_subject,
            'received_by': received_by
        }
        user_message_create(request=request, **kwargs)
    # send email
    kwargs = {
        'message_body': message_body,
        'message_subject': message_subject,
        'received_by': received_by
    }
    send_portal_mail_from_message(request=request, **kwargs)


def generate_user_messages_for_sandbox(request, experiment: AerpawExperiment):
    """
    UserMessage - required components (per message)
    - message_body     - string
    - message_owner    - int:user_id
    - message_subject  - string
    - received_by      - array of int:user_id
    """
    received_by_all = [m.id for m in experiment.experiment_members().all()]
    received_by_all.append(AerpawUser.objects.get(username=experiment.created_by).id)
    if experiment.state() == AerpawExperiment.ExperimentState.WAIT_SANDBOX_DEPLOY.value:
        # Submit to Testbed - button pressed by user - emulation required
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update for request to submit to sandbox for Experiment: {0}'.format(experiment.name)
        message_body = """
Your experiment {0} has been scheduled and is now awaiting execution in the Sandbox.

When the Sandbox Execution has started, you will receive another email.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
        
    elif experiment.state() == AerpawExperiment.ExperimentState.ACTIVE_SANDBOX.value:
        # Wait for Testbed deploy - session is scheduled and awaiting execution on testbed
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update - Experiment: {0} is now active in the sandbox'.format(experiment.name)
        message_body = """
Your experiment {0} is presently being executed in the Sandbox.

When the Sandbox Execution is complete, you will receive another email.
As noted in the AERPAW User Manual, this can take a variable amount of time.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))   
    
    elif experiment.state() == AerpawExperiment.ExperimentState.SAVING_SANDBOX.value:
        # Wait for Testbed deploy - session is scheduled and awaiting execution on testbed
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update - Experiment: {0} has returned from the sandbox'.format(experiment.name)
        message_body = """
Saving experiment: {0} As noted in the AERPAW User Manual, this can take a variable amount of time, from minutes to hours. """.format(experiment.name)
        
    elif experiment.state() == AerpawExperiment.ExperimentState.SAVED.value:
        # Wait for Testbed deploy - session is scheduled and awaiting execution on testbed
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Saving sandbox execution for Experiment: {0}'.format(experiment.name)
        message_body = """
Your experiment {0} has returned from Sandbox Execution.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))    
        
    else:
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update - Experiment: {0} has been canceled'.format(experiment.name)
        message_body = """
Sandbox Execution for experiment {0} has been canceled.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
        
    # send message
    received_by = set(received_by_all)
    for member in received_by:
        kwargs = {
            'message_body': message_body,
            'message_owner': member,
            'message_subject': message_subject,
            'received_by': received_by
        }
        user_message_create(request=request, **kwargs)
    # send email
    kwargs = {
        'message_body': message_body,
        'message_subject': message_subject,
        'received_by': received_by
    }
    send_portal_mail_from_message(request=request, **kwargs)


def generate_user_messages_for_emulation(request, experiment: AerpawExperiment):
    """
    UserMessage - required components (per message)
    - message_body     - string
    - message_owner    - int:user_id
    - message_subject  - string
    - received_by      - array of int:user_id
    """
    received_by_all = [m.id for m in experiment.experiment_members().all()]
    received_by_all.append(AerpawUser.objects.get(username=experiment.created_by).id)
    if experiment.state() == AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE.value:
        # Submit to Testbed - button pressed by user - emulation required
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update for request to submit to emulation for Experiment: {0}'.format(experiment.name)
        message_body = """
Your experiment, {0}, has been forwarded to AERPAW Ops for Emulation Execution.

When the Emulation Execution is scheduled, you will receive another email.
As noted in the AERPAW User Manual, this can take a variable amount of time, typically several days.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
    elif experiment.state() == AerpawExperiment.ExperimentState.WAIT_EMULATION_DEPLOY.value:
        # Submit to Testbed - button pressed by user - emulation required
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update for request to submit to emulation for Experiment: {0}'.format(experiment.name)
        message_body = """
Your experiment {0} has been scheduled and is now awaiting execution in Emulation.

When the Emulation Execution has started, you will receive another email.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
        
    elif experiment.state() == AerpawExperiment.ExperimentState.ACTIVE_EMULATION.value:
        # Wait for Testbed deploy - session is scheduled and awaiting execution on testbed
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update - Experiment: {0} is now active in the emulation'.format(experiment.name)
        message_body = """
Your experiment {0} is presently being executed in Emulation.

When the Emulation Execution is complete, you will receive another email.
As noted in the AERPAW User Manual, this can take a variable amount of time.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))   
        
    elif experiment.state() == AerpawExperiment.ExperimentState.SAVED.value:
        # Wait for Testbed deploy - session is scheduled and awaiting execution on testbed
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Saving emulation execution for Experiment: {0}'.format(experiment.name)
        message_body = """
Your experiment {0} has returned from Emulation Execution.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))    
        
    else:
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update - Experiment: {0} has been canceled'.format(experiment.name)
        message_body = """
Emulation Execution for experiment {0} has been canceled.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
        
    # send message
    received_by = set(received_by_all)
    for member in received_by:
        kwargs = {
            'message_body': message_body,
            'message_owner': member,
            'message_subject': message_subject,
            'received_by': received_by
        }
        user_message_create(request=request, **kwargs)
    # send email
    kwargs = {
        'message_body': message_body,
        'message_subject': message_subject,
        'received_by': received_by
    }
    send_portal_mail_from_message(request=request, **kwargs)


def generate_user_messages_for_testbed(request, experiment: AerpawExperiment):
    """
    UserMessage - required components (per message)
    - message_body     - string
    - message_owner    - int:user_id
    - message_subject  - string
    - received_by      - array of int:user_id
    """
    received_by_all = [m.id for m in experiment.experiment_members().all()]
    received_by_all.append(AerpawUser.objects.get(username=experiment.created_by).id)
    if experiment.state() == AerpawExperiment.ExperimentState.WAIT_TESTBED_SCHEDULE.value:
        # Submit to Testbed - button pressed by user - no emulation required
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Request to submit to testbed for Experiment: {0}'.format(experiment.name)
        message_body = """
Your request to submit your experiment {0} for testbed execution has been forwarded to AERPAW Ops.
Your experiment may require Emulation prior to opportunistic scheduling and subsequent execution on the Testbed.

When the Testbed Execution is complete, you will receive another email. 
As noted in the AERPAW User Manual, this can take a variable amount of time, typically several days.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
    elif experiment.state() == AerpawExperiment.ExperimentState.WAIT_EMULATION_SCHEDULE.value:
        # Submit to Testbed - button pressed by user - emulation required
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Request to submit to testbed for Experiment: {0} (Emulation Required)'.format(
            experiment.name)
        message_body = """
Your request to submit your experiment {0} for testbed execution has been forwarded to AERPAW Ops.
Your experiment requires Emulation prior to opportunistic scheduling and subsequent execution on the Testbed.

When the Testbed Execution is complete, you will receive another email. 
As noted in the AERPAW User Manual, this can take a variable amount of time, typically several days.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
    elif experiment.state() == AerpawExperiment.ExperimentState.WAIT_TESTBED_DEPLOY.value:
        # Wait for Testbed deploy - session is scheduled and awaiting execution on testbed
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update for request to submit to testbed for Experiment: {0}'.format(
            experiment.name)
        message_body = """
Your experiment {0} has been scheduled and is now awaiting execution on the Testbed.

When the Testbed Execution is complete, you will receive another email. 
As noted in the AERPAW User Manual, this can take a variable amount of time, typically several days.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
    elif experiment.state() == AerpawExperiment.ExperimentState.ACTIVE_TESTBED.value:
        # Active in Testbed - session is being actively executed on the testbed
        # - notify: experiment_members, operators
        received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
        message_subject = '[AERPAW] Update - Experiment: {0} is now active on the testbed'.format(
            experiment.name)
        message_body = """
Your experiment {0} is presently being executed on the Testbed.

When the Testbed Execution is complete, you will receive another email. 
As noted in the AERPAW User Manual, this can take a variable amount of time.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
    elif experiment.state() == AerpawExperiment.ExperimentState.SAVED.value:
        if experiment.experiment_flags == '010':
            # Testbed execution completed - experiment has returned from testbed
            # - notify: experiment_members, operators
            received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
            message_subject = '[AERPAW] Update - Experiment: {0} has returned from testbed'.format(
                experiment.name)
            message_body = """
Your experiment {0} has returned from testbed execution.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
        else:
            # Testbed execution cancelled - Testbed session has been cancelled
            # - notify: experiment_members, operators
            received_by_all = received_by_all + [u.id for u in AerpawUser.objects.filter(groups__in=[3]).all()]
            message_subject = '[AERPAW] Update - Experiment: {0} has been cancelled'.format(
                experiment.name)
            message_body = """
Testbed execution for experiment {0} has been cancelled.

Experiment ID: {1}
Experiment UUID: {2}
""".format(experiment.name, str(experiment.id), str(experiment.uuid))
    else:
        message_subject = '[AERPAW] Invalid state for Experiment: {0}'.format(experiment.name)
        message_body = """
Experiment: {0} is in an Invalid state
""".format(experiment.name)
    # send message
    received_by = set(received_by_all)
    for member in received_by:
        kwargs = {
            'message_body': message_body,
            'message_owner': member,
            'message_subject': message_subject,
            'received_by': received_by
        }
        user_message_create(request=request, **kwargs)
    # send email
    kwargs = {
        'message_body': message_body,
        'message_subject': message_subject,
        'received_by': received_by
    }
    send_portal_mail_from_message(request=request, **kwargs)

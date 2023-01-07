import os
from datetime import datetime, timezone
from uuid import uuid4

from django.core.mail import send_mail

from portal.apps.user_messages.models import AerpawUserMessage
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.users.models import AerpawRolesEnum, AerpawUser
from portal.apps.projects.models import AerpawProject
from portal.apps.experiments.models import AerpawExperiment


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
        print('here')
        # role
        if not user_request.get('response_date'):
            print('role request')
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
            print('role response')
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

Your request to join the Experiment: {1} has been forwarded to the owners of this project.
You will receive an email confirmation once one of the Project Owners has approved/denied this request.
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
    for owner in message_owner_ids:
        kwargs = {
            'message_body': message_body,
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
- AERPAW Acceptable Use Policy: https://sites.google.com/ncsu.edu/aerpaw-wiki/aerpaw-user-manual/2-experiment-web-portal/2-5-acceptable-use-policy-aup

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

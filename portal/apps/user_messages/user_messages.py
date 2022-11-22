import os
from datetime import datetime, timezone
from uuid import uuid4

from django.core.mail import send_mail

from portal.apps.user_messages.models import AerpawUserMessage
from portal.apps.users.models import AerpawUser


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
        AerpawUser.objects.filter(id=user_request.get('requested_by')).first().display_name,
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


def generate_new_user_welcome_message(request, user: AerpawUser):
    message_body = """
Hello {0},

Welcome to the AERPAW Portal
        
User manuals, tutorials, and other relevant documentation can be found at the following links; 
please refer to relevant instructions before attempting to use this Portal.

- AERPAW Main Site: https://aerpaw.org/
- AERPAW User Manual: https://sites.google.com/ncsu.edu/aerpaw-wiki/
- AERPAW Acceptable Use Policy: https://sites.google.com/ncsu.edu/aerpaw-wiki/aerpaw-user-manual/2-experiment-web-portal/2-5-acceptable-use-policy-aup
""".format(user.display_name)
    message_subject = '[AERPAW] Welcome {0} to the AERPAW portal!'.format(user.display_name)
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

import traceback, logging, datetime, os, uuid
from django.apps import apps
from django.utils import timezone
from uuid import uuid4

from portal.apps.error_handling.models import AerpawError, AerpawThread
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser

def portal_error_message(user: AerpawUser, *args, **kwargs) -> bool:
    print(f'kwargs {kwargs.get("message_subject")}')
    aerpaw_user_message = apps.get_model('user_messages', 'AerpawUserMessage')
    try:
        print(f'aerpaw user message {aerpaw_user_message}')
        user = AerpawUser.objects.get(id=user.id)
        received_by = [user]
        # create user message
        user_message = aerpaw_user_message()
        user_message.created = timezone.now()
        user_message.created_by = user.username
        user_message.message_body = kwargs.get('message_body', None)
        user_message.message_owner = user
        user_message.message_subject = kwargs.get('message_subject', None)
        user_message.modified = timezone.now()
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

def aerpaw_error_message(exc: Exception, user: AerpawUser, error: AerpawError, msg: str=None) -> str:
    # Use the custom message if there is one
    if msg is not None:
        message = f'Error #: {error.id}<br>{msg}<hr class="w-50 text-danger">'
    else:
        # Determines what the message will say by the user's group(s)
        # Needs an AerpawError to reference the id in the message
        if user.is_operator() or user.is_site_admin():
            if hasattr(exc, 'detail'):
                message = f'Error #: {error.id}<br>{exc.detail}<hr class="w-50 text-danger">'
            else:
                message = f'Error #: {error.id}<br>{exc}<hr class="w-50 text-danger">'
        else:
            message = f'An Error has occured! Id# {error.id}<br> If this error persists, please contact the Aerpaw Ops Team.<br><a class="btn btn-sm btn-outline-danger" href="mailto:cjr47@cornell.edu?subject=Error#%20{error.id}"><i class="fas fa-envelope-square"></i></a><hr class="w-50 text-danger">'

    message_components = {
        'message_body': message, 
        'message_owner':user.id, 
        'message_subject':f'Error# {error.id}',
        'recieved_by':user.id
        }
    portal_error_message(user, None, **message_components)
    
    return message

def new_error(exc: Exception, user: AerpawUser, msg: str=None) -> AerpawError:

    # first create an error instance to be able to reference the id in the message
    error = AerpawError(
        user=user,
        type=type(exc).__name__,
        traceback=traceback.format_exc(),
        uuid=uuid.uuid4()
    )
    # create the correct message depending on user group
    error.save()
    error.message = aerpaw_error_message(exc, user, error, msg)
    error.save()

    # Reduce the stored errors in the database. All errors older than 90 days are deleted
    reduce_stored_errors()

    return error

def start_aerpaw_thread(user: AerpawUser, experiment:AerpawExperiment, action: AerpawThread.ThreadActions) -> AerpawThread:
    new_thread = AerpawThread(
        user=user,
        uuid=uuid4(),
        experiment=experiment,
        displayed=False,
        action=action,
    )
    new_thread.save()
    print(f'New AerpawThread: thread# {new_thread.id}')
    return new_thread

def end_aerpaw_thread(thread: AerpawThread, exit_code, response) -> None:
    
    thread.thread_end = timezone.now()
    thread.exit_code = exit_code
    thread.response = response
    thread.save()
    message_components = {
        'message_body': thread.message, 
        'message_owner':thread.user.id, 
        'message_subject':f'{thread.get_action_display()} for Experiment: {thread.experiment.id}',
        'recieved_by':thread.user.id
        }
    portal_error_message(thread.user, None, **message_components)
    print(f'AerpawThread ended: thread# {thread.id}')

def add_error_to_thread(thread: AerpawThread, error: AerpawError):
    thread.error.add(error)
    thread.is_error = True
    thread.save()
    print(f'added error: {error} to AerpawThread: {thread}')

def reduce_stored_errors():
    # finds and deletes all errors that are over 90 days old
    today = timezone.now()
    timedelta_90_days = datetime.timedelta(days=-90)
    cut_off_date = today + timedelta_90_days
    errors = AerpawError.objects.filter(datetime__lte=(cut_off_date))
    for error in errors:
        error.delete()
    

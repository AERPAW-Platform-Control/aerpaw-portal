import traceback, logging, datetime, os, uuid
from django.apps import apps
from django.utils import timezone
from uuid import uuid4

from portal.apps.error_handling.api.error_messages import AerpawErrorMessageHandler
from portal.apps.error_handling.models import AerpawError, AerpawThread, AerpawErrorGroup
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser


def new_error(exc: Exception, user: AerpawUser, msg: str=None) -> AerpawError:
    handler = AerpawErrorMessageHandler()
    # first create an error instance to be able to reference the id in the message
    error = AerpawError(
        user=user,
        type=type(exc).__name__,
        traceback=traceback.format_exception(exc),
        uuid=uuid.uuid4()
    )
    # create the correct message depending on user group
    error.save()

    # Reduce the stored errors in the database. All errors older than 90 days are deleted
    reduce_stored_errors()

    return error

def new_error_group(user, view, errors):
    # first create an error instance to be able to reference the id in the message
    err_group = AerpawErrorGroup(
        user=user,
        view_name=view
    )
    # create the correct message depending on user group
    err_group.save()
    err_group.errors.add(*errors)
    err_group.save()

    return err_group


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
    AerpawErrorMessageHandler.portal_error_message(thread.user, None, **message_components)
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
    err_group = AerpawErrorGroup.objects.filter(datetime__lte=(cut_off_date))
    for error in errors:
        error.delete()
    for group in err_group:
        if group.errors.all().count() == 0:
            err_group.delete()
    

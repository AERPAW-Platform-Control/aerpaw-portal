import os
from django.apps import apps
from django.utils import timezone
from uuid import uuid4

from portal.apps.error_handling.models import AerpawError, AerpawThread, AerpawErrorGroup
from portal.apps.users.models import AerpawUser
from portal.server.settings import MOCK_OPS

class AerpawErrorMessageHandler():
    error_groups = {
        'one':['PermissionDenied'],
        'two':['NotFound', 'Http404', 'DoesNotExist'],
        'three':['ValidationError']
    }

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

    def aerpaw_error_message(self, exc: Exception, user: AerpawUser, error: AerpawError, msg: str=None) -> str:
        
        # Determines what the message will say by the user's group(s)
        # Needs an AerpawError to reference the id in the message
        if user.is_operator() or user.is_site_admin():
            if msg is not None:
                message = f'Error #{error.id}: {msg}'
            elif hasattr(exc, 'detail'):
                message = f'Error #{error.id}<br>{exc.detail}'
            else:
                message = f'Error #{error.id}<br>{exc}'
        else:
            email = 'aerpaw-operations@ncsu.edu'
            if MOCK_OPS:
                email = 'cjrober5@ncsu.edu'
            message = f'Error #{error.id}: An Error has occured!<br> If this error persists, please <a class="btn btn-sm btn-outline-danger" href="mailto:{email}?subject=Error#%20{error.id}">click here to email the Aerpaw Ops Team <i class="fa fa-paper-plane"></i></a>'

        message_components = {
            'message_body': message, 
            'message_owner':user.id, 
            'message_subject':f'Error# {error.id}',
            'recieved_by':user.id
            }
        self.portal_error_message(user, None, **message_components)
        
        return message
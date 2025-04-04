from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from rest_framework.request import QueryDict, Request

from portal.apps.credentials.api.viewsets import CredentialViewSet
from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.profiles.api.viewsets import UserProfileViewSet
from portal.apps.user_messages.api.viewsets import UserMessageViewSet
from portal.apps.user_requests.api.viewsets import UserRequestViewSet
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.users.api.viewsets import UserViewSet
from portal.apps.users.models import AerpawRolesEnum, AerpawUser
from portal.server.download_utils import download_db_credential_public_key, download_db_user_tokens
from portal.server.settings import DEBUG


@csrf_exempt
def profile(request):
    """
    :param request:
    :return:
    """
    message = None
    # get user from request.user.id - redirect if not found
    try:
        user = AerpawUser.objects.get(pk=request.user.id)
    except Exception as exc:
        print(exc)
        new_error(exc, request.user)
        return redirect('user_not_found')
    if request.method == 'POST':
        try:
            if request.POST.get('display_name'):
                # update user: display_name
                u_api_request = Request(request=HttpRequest())
                u = UserViewSet(request=u_api_request)
                u_api_request.user = request.user
                u_api_request.method = 'PUT'
                u_api_request.data.update(
                    {'display_name': request.POST.get('display_name')})
                resp = u.update(request=u_api_request, pk=user.id)
            if 'employer' in list(request.POST.keys()):
                # update profile: employer, position and research_field
                u_api_request = Request(request=HttpRequest())
                u = UserProfileViewSet(request=u_api_request)
                u_api_request.user = request.user
                u_api_request.method = 'PUT'
                u_api_request.data.update(
                    {
                        'employer': request.POST.get('employer', ''),
                        'position': request.POST.get('position', ''),
                        'research_field': request.POST.get('research_field', '')
                    })
                resp = u.update(request=u_api_request, pk=user.profile.id)
            if request.POST.get('generate_tokens'):
                u_api_request = Request(request=HttpRequest())
                u = UserViewSet(request=u_api_request)
                u_api_request.user = request.user
                u_api_request.method = 'GET'
                u_api_request.query_params.update({'generate': 'true'})
                resp = u.tokens(request=u_api_request, pk=user.id)
            if request.POST.get('refresh_access_token'):
                u_api_request = Request(request=HttpRequest())
                u = UserViewSet(request=u_api_request)
                u_api_request.user = request.user
                u_api_request.method = 'GET'
                u_api_request.query_params.update({'refresh': 'true'})
                resp = u.tokens(request=u_api_request, pk=user.id)
            if request.POST.get('download_credential'):
                try:
                    response = download_db_credential_public_key(
                        user_id=user.id, credential_id=int(request.POST.get('download_credential'))
                    )
                    return response
                except Exception as exc:
                    error = new_error(exc, request.user)
                    message = error.message
            if request.POST.get('delete_credential'):
                c_api_request = Request(request=HttpRequest())
                c = CredentialViewSet(request=c_api_request)
                c_api_request.user = request.user
                c_api_request.method = 'DELETE'
                c.destroy(request=c_api_request, pk=request.POST.get('delete_credential'))
            if request.POST.get('download_tokens'):
                try:
                    response = download_db_user_tokens(user_id=user.id)
                    return response
                except Exception as exc:
                    error = new_error(exc, request.user)
                    message = error.message
            if request.POST.get('request_role_experimenter'):
                ur_api_request = Request(request=HttpRequest())
                ur = UserRequestViewSet(request=ur_api_request)
                ur_api_request.user = request.user
                ur_api_request.method = 'POST'
                ur_api_request.data.update(
                    {'request_type': AerpawUserRequest.RequestType.ROLE.value,
                     'request_type_id': request.user.id,
                     'request_note': '[{0}] - role request'.format(AerpawRolesEnum.EXPERIMENTER.value)})
                resp = ur.create(request=ur_api_request)
                return HttpResponseRedirect(reverse('profile'))
            if request.POST.get('request_role_pi'):
                print(f'request of PI')
                ur_api_request = Request(request=HttpRequest())
                ur = UserRequestViewSet(request=ur_api_request)
                ur_api_request.user = request.user
                ur_api_request.method = 'POST'
                ur_api_request.data.update(
                    {'request_type': AerpawUserRequest.RequestType.ROLE.value,
                     'request_type_id': request.user.id,
                     'request_note': '[{0}] - role request'.format(AerpawRolesEnum.PI.value)})
                resp = ur.create(request=ur_api_request)
                return HttpResponseRedirect(reverse('profile'))
        except Exception as exc:
            error = new_error(exc, request.user)
            message = error.message
    try:
        # user data
        api_request = Request(request=HttpRequest())
        api_request.user = request.user
        api_request.method = 'GET'
        u = UserViewSet(request=api_request)
        user_credentials = u.credentials(request=request, pk=request.user.id).data
        user_data = u.retrieve(request=request, pk=request.user.id).data
        user_tokens = u.tokens(request=api_request, pk=request.user.id).data

        # user profile
        up = UserProfileViewSet(request=api_request)
        user_profile = up.retrieve(request=request, pk=user.profile.id).data

        # modify query_params to get requests and messages data
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update({'user_id': user.id, 'show_read': False, 'show_deleted': False})

        # user requests data
        ur = UserRequestViewSet(request=request)
        user_requests = dict(ur.list(request=request).data)

        # user messages data
        um = UserMessageViewSet(request=request)
        user_messages = dict(um.list(request=request).data)
        unread_message_count = um.unread_message_count(request=request)
        
    except Exception as exc:
        print('Exception found in profiles.views profile ', exc)
        new_error(exc, request.user)
        
    return render(request,
                  'profile.html',
                  {
                      'user': user,
                      'user_data': user_data,
                      'user_profile': user_profile,
                      'user_tokens': user_tokens,
                      'user_credentials': user_credentials,
                      'user_messages': user_messages,
                      'user_requests': user_requests,
                      'unread_message_count': unread_message_count,
                      'message': message,
                      'debug': DEBUG
                  })


def session_expired(request):
    """
    :param request:
    :return:
    """
    print('session_expired')
    return render(request,
                  'login.html',
                  {
                      'session_expired': True
                  })


def user_not_found(request):
    """
    :param request:
    :return:
    """
    print('user_not_found')
    return render(request, 'user_not_found.html')

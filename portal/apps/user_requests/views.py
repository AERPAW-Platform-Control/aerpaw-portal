import os, json
from urllib.parse import parse_qs, urlparse

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, QueryDict, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.request import Request

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.user_requests.api.viewsets import UserRequestViewSet
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.user_requests.user_requests import approve_user_role_request, deny_user_role_request
from portal.server.settings import DEBUG, REST_FRAMEWORK
from portal.apps.users.google_group_manager import credentials_to_dict

SCOPES = ["https://www.googleapis.com/auth/admin.directory.group.member", "https://www.googleapis.com/auth/admin.directory.group", 'https://www.googleapis.com/auth/apps.groups.settings']
SERVICE_ACCOUNT_KEY = 'service_account_key.json'
CLIENT_ID = '20527554357-6ur6tdml35k0g54m5mhg6bptetc2580e.apps.googleusercontent.com'
OAUTH_REDIRECT_URI = 'http://127.0.0.1:8000/oauth2callback/'
CLIENT_SECRET = 'client_secret.apps.googleusercontent.com.json'
TOKEN_FILE = 'oauth2_user_token.json'
GROUP_NAME = "groups/02lwamvv2t79se1"

@csrf_exempt
@login_required
def user_role_reqeust_list(request):
    message = None
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        if request.method == 'POST':
            if request.POST.get('approve_request_id'):
                if approve_user_role_request(request_id=int(request.POST.get('approve_request_id'))):
                    ur_api_request = Request(request=HttpRequest())
                    ur = UserRequestViewSet(request=ur_api_request)
                    ur_api_request.user = request.user
                    ur_api_request.method = 'PUT'
                    ur_api_request.data.update(
                        {'is_approved': True,
                         'response_note': request.POST.get('response_note', None)})
                    resp = ur.update(request=ur_api_request, pk=request.POST.get('approve_request_id'))
            if request.POST.get('deny_request_id'):
                if deny_user_role_request(request_id=int(request.POST.get('deny_request_id'))):
                    ur_api_request = Request(request=HttpRequest())
                    ur = UserRequestViewSet(request=ur_api_request)
                    ur_api_request.user = request.user
                    ur_api_request.method = 'PUT'
                    ur_api_request.data.update(
                        {'is_approved': False,
                         'response_note': request.POST.get('response_note', None)})
                    resp = ur.update(request=ur_api_request, pk=request.POST.get('deny_request_id'))
        data_dict = {'request_type': AerpawUserRequest.RequestType.ROLE.value}
        if request.GET.get('page'):
            data_dict['page'] = request.GET.get('page')
            current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        ur = UserRequestViewSet(request=request)
        user_requests = ur.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if user_requests.data:
            user_requests = dict(user_requests.data)
            prev_url = user_requests.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    new_error(exc, request.user)
                    prev_page = 1
            next_url = user_requests.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    new_error(exc, request.user)
                    next_page = 1
            count = int(user_requests.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        else:
            user_requests = {}
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        error = new_error(exc, request.user)
        message = error.message
        user_requests = {}
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'user_role_request_list.html',
                  {
                      'user': request.user,
                      'user_requests': user_requests,
                      'item_range': item_range,
                      'message': message,
                      'next_page': next_page,
                      'prev_page': prev_page,
                      'search': search_term,
                      'count': count,
                      'debug': DEBUG
                  })

@login_required
def join_google_group(request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET,
        scopes = ['https://www.googleapis.com/auth/cloud-identity.groups', 'https://www.googleapis.com/auth/apps.groups.settings'],
        redirect_uri=OAUTH_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    request.session['oauth_state'] = state
    print(f'authorization url= {authorization_url}')
    print(f'state= {state}')
    return redirect(authorization_url)

def oauth2_callback(request):
    # Redirect to a view that adds users to the group
    try:
        state = request.session.pop('oauth_state', '')
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/cloud-identity.groups', 'https://www.googleapis.com/auth/apps.groups.settings'],
            redirect_uri=OAUTH_REDIRECT_URI,
            state=state
        )

        flow.fetch_token(authorization_response=request.build_absolute_uri())

        credentials = flow.credentials
        with open(TOKEN_FILE, "w") as token_file:
            json.dump(credentials_to_dict(credentials), token_file, indent=4)
        print(f'credentials= {credentials}')
        request.session['google_credentials'] = credentials_to_dict(credentials)
    except Exception as exc:
        print(f'oauth2_callback exc= {exc}')
    return redirect('profile')

def add_user_to_group(request):
    print('Adding user to group')
    credentials = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/cloud-identity.groups'])
    print(f'Got Credentials: {credentials}')
    if not credentials:
        print('Cannot add user to group! Credentials not found')
        return redirect('/google-login/')  # Redirect to login if not authenticated

    service = build('cloudidentity', 'v1', credentials=credentials)
    print(f'Built service: {service}')
    user_email = "robertschristopher5060@gmail.com"

    group_membership = {
        'preferredMemberKey': {'id': user_email},
        'roles': [{'name': 'MEMBER'}]
    }

    try:
        request = service.groups().memberships().create(
            parent=GROUP_NAME,
            body=group_membership
        )
        print(f'Created request: {request}')
        response = request.execute()
        print(f'User added! Response= {response}\n')
        return JsonResponse({"message": f"Added user {user_email}.", "response": response, 'moderation_settings_response':json_response})
    except Exception as e:
        return f"Error: {str(e)}"
    
def list_group_members(request):
    credentials = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/cloud-identity.groups'])
    service = build('cloudidentity', 'v1', credentials=credentials)
    
    request = service.groups().memberships().list(parent=GROUP_NAME)
    response = request.execute()
    print(f'Response= {response.keys()}')
    for member in response.get("memberships"):
        print(f"Member= {member['preferredMemberKey']['id']}")
    return response.get("memberships", [])


import os, json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from portal.apps.google_group.group_dashboard import credentials_to_dict

SCOPES = ["https://www.googleapis.com/auth/admin.directory.group.member", "https://www.googleapis.com/auth/admin.directory.group", 'https://www.googleapis.com/auth/apps.groups.settings']
SERVICE_ACCOUNT_KEY = 'service_account_key.json'
CLIENT_ID = '20527554357-6ur6tdml35k0g54m5mhg6bptetc2580e.apps.googleusercontent.com'
OAUTH_REDIRECT_URI = 'http://127.0.0.1:8000/oauth2callback/'
CLIENT_SECRET = 'client_secret.apps.googleusercontent.com.json'
TOKEN_FILE = 'oauth2_user_token.json'
GROUP_NAME = "groups/02lwamvv2t79se1"

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
        return JsonResponse({"message": f"Added user {user_email}.", "response": response})
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


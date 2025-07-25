import googleapiclient
from django.http import JsonResponse

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .models import GoogleGroupMembership
from portal.apps.error_handling.error_dashboard import new_error

TOKEN_FILE = 'oauth2_user_token.json'
GROUP_NAME = "groups/02lwamvv2t79se1"

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def add_user_to_group(request):
    print('\n\n\n')
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.apps.googleusercontent.com.json',
            scopes=['https://www.googleapis.com/auth/cloud-identity.groups']
        )
        credentials = flow.run_local_server(port=8080)
        #credentials = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/cloud-identity.groups'])
        print(f'credentials {credentials}')
    except Exception as exc:
        print('Cannot add user to group! Credentials not found')
        new_error(exc, request.user)

    service = build('cloudidentity', 'v1', credentials=credentials)
    #user_email = str(request.user.email)
    #user_email = 'cmv303@nyu.edu'
    #user_email='cjrober5@outlook.com'
    user_email='cjroberts5@icloud.com'
    group_membership = {
        'preferredMemberKey': {
            'id': user_email,
            },
        'roles': [{'name': 'MEMBER'}],
        
    }

    try:
        request = service.groups().memberships().create(
            parent=GROUP_NAME,
            body=group_membership
        ).execute()
        return True
    except Exception as exc:
        error = new_error(exc, request.user)
        print('\n\n\n')
        print(f'ERROR!\n{error.traceback}')
        print('\n\n\n')
        return False
  
    

def user_gave_consent(request):
    try:
        user_google_group = GoogleGroupMembership.objects.get(user=request.user)
        user_google_group.consent_asked = True
        user_google_group.consent_given = True
        user_google_group.member = add_user_to_group(request)
        user_google_group.save()
    except Exception as exc:
        error = new_error(exc, request.user)
        print(f'{error.traceback}')

def user_declined_group(request):
    try:
        user_google_group = GoogleGroupMembership.objects.get(user=request.user)
        user_google_group.consent_asked = True
        user_google_group.consent_given = False
        user_google_group.member = False
        user_google_group.save()
    except Exception as exc:
        error = new_error(exc, request.user)
        print(f'{error.traceback}')

def list_group_members(request):
    credentials = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/cloud-identity.groups'])
    service = build('cloudidentity', 'v1', credentials=credentials)    
    request = service.groups().memberships().list(parent=GROUP_NAME)
    response = request.execute()
    member_emails = [member['preferredMemberKey']['id'] for member in response.get("memberships")]
    return member_emails
from django.http import JsonResponse

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

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
    print('Adding user to group')
    credentials = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/cloud-identity.groups'])
    print(f'Got Credentials: {credentials}')
    if not credentials:
        print('Cannot add user to group! Credentials not found')
        

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
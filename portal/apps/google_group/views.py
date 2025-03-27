import os, json, webbrowser
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.google_group.models import GoogleGroupMembership
from portal.apps.google_group.group_dashboard import credentials_to_dict, user_gave_consent, user_declined_group, list_group_members

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

@login_required
def user_consent_view(request):
    print('user consent view')
    print(f'request.POST= {request.POST}')
    if request.method == 'POST':
            if 'join_group' in request.POST:
                print(f'user email= {request.user.email}')
                user_gave_consent(request)
                webbrowser.open('https://groups.google.com/a/ncsu.edu/g/group-aerpaw-users/', new=2)
                return redirect('home')
            if 'decline_group' in request.POST:
                user_declined_group(request)
                return redirect('home')

@login_required
def google_group_forum(request):
    prevent_navigation = False
    try:
        

        google_group = GoogleGroupMembership.objects.get(user=request.user)
        if google_group.member == True:
            return redirect('https://groups.google.com/a/ncsu.edu/g/group-aerpaw-users/')
        if google_group.consent_given == False:
            ask_consent = True

        if google_group.consent_asked == False:
            prevent_navigation = True
            print(f'prevent navigation= {prevent_navigation}')
    except Exception as exc:
        new_error(exc, request.user)
        ask_consent = '<p>There was a problem signing up for the forum. Please directly visit the <a href="https://groups.google.com/a/ncsu.edu/g/group-aerpaw-users">forum</a> to sign up.</p>'
        
        
    context = {
        'ask_consent':ask_consent,
        'prevent_navigation': prevent_navigation,
    }
    return render(request, 'google_group_consent.html', context)
        



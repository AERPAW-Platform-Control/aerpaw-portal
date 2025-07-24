import os, json, webbrowser
import google_auth_oauthlib.flow
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.google_group.models import GoogleGroupMembership
from portal.apps.google_group.group_dashboard import credentials_to_dict, user_gave_consent, user_declined_group, list_group_members

SCOPES = [
    "https://www.googleapis.com/auth/apps.groups.settings",
    "https://www.googleapis.com/auth/cloud-identity.groups",
]
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
        scopes = SCOPES,
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

def start_flow(request):
    request.session.pop('credentials', None)
    request.session.pop('state', None)
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.apps.googleusercontent.com.json',
        scopes=SCOPES,
        )
    flow.redirect_uri = OAUTH_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['oauth_state'] = state
    return authorization_url

def oauth2_callback(request):
    # Redirect to a view that adds users to the group
    try: 
        state = request.session.get('oauth_state')
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET,
            scopes=SCOPES,
            state=state
        )
        
        flow.redirect_uri = request.build_absolute_uri(reverse('oauth2_callback'))
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        with open(TOKEN_FILE, "w") as token_file:
            json.dump(credentials_to_dict(credentials), token_file, indent=4)
        request.session['google_credentials'] = credentials_to_dict(credentials)
    except Exception as exc:
        print()
        print(f'EXCEPTION oauth2_callback= {exc}')
        print()
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
    return render(request, 'google_group/google_group_consent.html', context)
        



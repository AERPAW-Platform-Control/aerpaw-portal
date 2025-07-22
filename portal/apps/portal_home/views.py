from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import Flow
from portal.apps.google_group.group_dashboard import list_group_members
from portal.apps.google_group.views import oauth2_callback, start_flow
from portal.apps.google_group.models import GoogleGroupMembership

@login_required
def home_view(request):
    
    user = request.user
    print(f'user email: {user.email}')
    google_group, created = GoogleGroupMembership.objects.get_or_create(user=user)
    is_member = user.email in list_group_members(request)
    print(f'is_member: {is_member}')

    # If the google membership object has just been created, save the user's membership status.
    if created:
        google_group.member=is_member
        google_group.save()

    # If the user is:
    #  - already a member 
    #    OR 
    #  - has already been asked to be a member and declined
    # Return them to the home page
    if google_group.member == True\
        or google_group.consent_asked == True\
            or is_member == True:
        context={}
        return render(request, 'home.html', context)
    
    # If the user is:
    # - not a member
    #   AND
    # - has not been asked if they want to be a member 
    # Ask them to join the Google Group
    elif google_group.consent_asked == False:
        return redirect('forum')

    
    
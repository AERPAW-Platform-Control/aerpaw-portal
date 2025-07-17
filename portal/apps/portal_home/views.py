from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import Flow
from portal.apps.google_group.group_dashboard import list_group_members
from portal.apps.google_group.views import oauth2_callback, start_flow
from portal.apps.google_group.models import GoogleGroupMembership

@login_required
def home_view(request):
    
    user = request.user
    google_group, created = GoogleGroupMembership.objects.get_or_create(user=user)
    is_member = user.email in list_group_members(request)
    if created:
        google_group.member=is_member
        google_group.save()

    if google_group.member == False and google_group.consent_asked == False:
        return redirect('forum')

    context={}

    return render(request, 'home.html', context)
    
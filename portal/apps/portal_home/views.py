from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from portal.apps.google_group.group_dashboard import list_group_members
from portal.apps.google_group.models import GoogleGroupMembership

@login_required
def home_view(request):
    user = request.user
    google_group = GoogleGroupMembership.objects.filter(user=user).first()
    ask_consent = False
    current_members = list_group_members(request)
    is_member = user.email in current_members
    print(f'is member= {is_member}')
    if not google_group:
        google_group = GoogleGroupMembership(
            user=user,
            consent_asked=False,
            consent_given=False,
            member=user.email in current_members
        )
        google_group.save()

    if google_group.member == False and google_group.consent_asked == False:
        return redirect('forum')

    context={}

    return render(request, 'home.html', context)
    
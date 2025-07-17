from django.urls import path
from portal.apps.google_group.views import join_google_group, oauth2_callback, user_consent_view, google_group_forum

urlpatterns = [
    path('join-google-group', join_google_group, name='join_google_group'),
    path('add-user-google-group', user_consent_view, name='user_consent_view'),
    path('forum-user-google-group', google_group_forum, name='forum'),
    path('oauth2callback', oauth2_callback, name="goauth2_callback"),
]
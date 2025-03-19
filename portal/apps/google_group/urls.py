from django.urls import path
from portal.apps.google_group.views import join_google_group, oauth2_callback, add_user_to_group

urlpatterns = [
    path('join-google-group', join_google_group, name='join_google_group'),
    path('add-user-google-group', add_user_to_group, name='add_user_google_group'),
]
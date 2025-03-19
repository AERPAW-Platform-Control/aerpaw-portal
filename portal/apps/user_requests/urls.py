from django.urls import path

from portal.apps.user_requests.views import user_role_reqeust_list, join_google_group, oauth2_callback, add_user_to_group

urlpatterns = [
    path('roles', user_role_reqeust_list, name='user_role_request_list'),
    path('join-google-group', join_google_group, name='join_google_group'),
    path('add-user-google-group', add_user_to_group, name='add_user_google_group'),
]

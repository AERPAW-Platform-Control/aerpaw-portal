from django.urls import path

from portal.apps.user_requests.views import user_role_reqeust_list

urlpatterns = [
    path('roles', user_role_reqeust_list, name='user_role_request_list'),
]

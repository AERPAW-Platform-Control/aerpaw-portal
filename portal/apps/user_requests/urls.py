from django.urls import path

from portal.apps.user_requests.views import user_role_reqeust_list

urlpatterns = [
    path('roles', user_role_reqeust_list, name='user_role_request_list'),
    # path('create', project_create, name='project_create'),
    # path('<int:project_id>', project_detail, name='project_detail'),
    # path('<int:project_id>/edit', project_edit, name='project_edit'),
    # path('<int:project_id>/members', project_members, name='project_members'),
    # path('<int:project_id>/owners', project_owners, name='project_owners'),
]

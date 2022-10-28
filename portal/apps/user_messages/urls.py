from django.urls import path

from portal.apps.user_messages.views import user_message_detail, user_message_list

urlpatterns = [
    path('', user_message_list, name='user_message_list'),
    # path('create', project_create, name='project_create'),
    path('<int:user_message_id>', user_message_detail, name='user_message_detail'),
    # path('<int:project_id>/edit', project_edit, name='project_edit'),
    # path('<int:project_id>/members', project_members, name='project_members'),
    # path('<int:project_id>/owners', project_owners, name='project_owners'),
]

from django.urls import path

from portal.apps.credentials.views import credential_add, credential_create, credential_detail, credential_edit, \
    credential_list

urlpatterns = [
    path('', credential_list, name='credential_list'),
    path('add', credential_add, name='credential_add'),
    path('create', credential_create, name='credential_create'),
    path('download', credential_create, name='credential_download'),
    path('<int:credential_id>', credential_detail, name='credential_detail'),
    path('<int:credential_id>/edit', credential_edit, name='credential_edit'),
]

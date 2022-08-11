from django.urls import path

from portal.apps.credentials.views import credential_create, credential_detail, credential_edit, credential_list

urlpatterns = [
    path('', credential_list, name='credential_list'),
    path('create', credential_create, name='credential_create'),
    path('<int:credential_id>', credential_detail, name='credential_detail'),
    path('<int:credential_id>/edit', credential_edit, name='credential_edit'),
]

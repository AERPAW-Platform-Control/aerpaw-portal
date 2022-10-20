from django.urls import path

from portal.apps.credentials.views import credential_add, credential_create

urlpatterns = [
    path('add', credential_add, name='credential_add'),
    path('create', credential_create, name='credential_create'),
    path('download', credential_create, name='credential_download'),
]

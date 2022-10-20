from django.urls import path

from portal.apps.experiment_files.views import experiment_file_create, experiment_file_detail, experiment_file_edit, \
    experiment_file_list

urlpatterns = [
    path('', experiment_file_list, name='experiment_file_list'),
    path('create', experiment_file_create, name='experiment_file_create'),
    path('<int:file_id>', experiment_file_detail, name='experiment_file_detail'),
    path('<int:file_id>/edit', experiment_file_edit, name='experiment_file_edit'),
]

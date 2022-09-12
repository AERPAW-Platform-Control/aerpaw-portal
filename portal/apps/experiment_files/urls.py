from django.urls import path

from portal.apps.experiment_files.views import experiment_file_create, experiment_file_detail, experiment_file_edit, \
    experiment_file_list

urlpatterns = [
    path('', experiment_file_list, name='experiment_file_list'),
    path('create', experiment_file_create, name='experiment_file_create'),
    path('<int:file_id>', experiment_file_detail, name='experiment_file_detail'),
    path('<int:file_id>/edit', experiment_file_edit, name='experiment_file_edit'),
    #     path('<int:experiment_id>/members', experiment_members, name='experiment_members'),
    #     path('<int:experiment_id>/resources', experiment_resource_list, name='experiment_resource_list'),
    #     path('<int:experiment_id>/resource-targets', experiment_resource_targets,
    #          name='experiment_resource_targets'),
    #     path('<int:experiment_id>/resource-targets/<int:canonical_experiment_resource_id>/edit',
    #          experiment_resource_target_edit,
    #          name='experiment_resource_target_edit'),
]

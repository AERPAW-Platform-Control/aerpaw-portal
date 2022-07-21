from django.urls import path

from portal.apps.experiments.views import experiment_create, experiment_detail, experiment_edit, experiment_list, \
    experiment_members, experiment_resource_definitions, experiment_resource_list

urlpatterns = [
    path('', experiment_list, name='experiment_list'),
    path('create', experiment_create, name='experiment_create'),
    path('<int:experiment_id>', experiment_detail, name='experiment_detail'),
    path('<int:experiment_id>/edit', experiment_edit, name='experiment_edit'),
    path('<int:experiment_id>/members', experiment_members, name='experiment_members'),
    path('<int:experiment_id>/resources', experiment_resource_list, name='experiment_resource_list'),
    path('<int:experiment_id>/resource-definitions', experiment_resource_definitions,
         name='experiment_resource_definitions'),
]

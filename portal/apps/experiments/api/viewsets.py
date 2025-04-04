from uuid import uuid4

from django.db.models import Q
from django.shortcuts import get_object_or_404
from itertools import chain
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, NotFound, PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.experiment_files.api.serializers import ExperimentFileSerializerDetail
from portal.apps.experiment_files.models import ExperimentFile
from portal.apps.experiments.api.experiment_states import is_valid_transition, transition_experiment_state
from portal.apps.experiments.api.serializers import CanonicalExperimentResourceSerializer, ExperimentSerializerDetail, \
    ExperimentSerializerList, ExperimentSerializerState, OnDemandSessionSerializerDetail, \
    ScheduledSessionSerializerDetail, OnDemandSessionSerializerList, ScheduledSessionSerializerList, UserExperimentSerializer
from portal.apps.experiments.models import AerpawExperiment, CanonicalExperimentResource, OnDemandSession, \
    UserExperiment, ScheduledSession
from portal.apps.operations.models import CanonicalNumber, get_current_canonical_number, \
    increment_current_canonical_number
from portal.apps.projects.models import AerpawProject
from portal.apps.resources.api.serializers import ResourceSerializerDetail
from portal.apps.resources.models import AerpawResource
from portal.apps.user_messages.user_messages import generate_user_messages_from_experiment_membership
from portal.apps.users.models import AerpawUser

#from portal.apps.experiments.api.experiment_utils import to_retired	#Experimental

# constants
EXPERIMENT_MIN_NAME_LEN = 5
EXPERIMENT_MIN_DESC_LEN = 5


class ExperimentViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    AERPAW Experiments
    - paginated list
    - retrieve one
    - create
    - update
    - delete
    - resources
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AerpawExperiment.objects.all().order_by('name').distinct()
    serializer_class = ExperimentSerializerDetail

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        user = self.request.user
        if search:
            if user.is_operator():
                queryset = AerpawExperiment.objects.filter(
                    is_deleted=False, name__icontains=search).order_by('name').distinct()
            else:
                queryset = AerpawExperiment.objects.filter(
                    Q(is_deleted=False, name__icontains=search) &
                    (Q(project__project_membership__email__in=[user.email]) | Q(project__project_creator=user))
                ).order_by('name').distinct()
        else:
            if user.is_operator():
                queryset = AerpawExperiment.objects.filter(is_deleted=False).order_by('name').distinct()
            else:
                queryset = AerpawExperiment.objects.filter(
                    Q(is_deleted=False) &
                    (Q(project__project_membership__email__in=[user.email]) | Q(project__project_creator=user))
                ).order_by('name').distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list experiments as paginated results
        - canonical_number       - int
        - created_date           - string
        - description            - string
        - experiment_creator     - user_ID
        - experiment_id          - int
        - experiment_state       - string
        - is_canonical           - boolean
        - is_retired             - boolean
        - name                   - string
        - project_id             - int

        Permission:
        - user is_experiment_project_member OR
        - user is_experiment_project_creator OR
        - user is_operator
        """
        if request.user.is_active:
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = ExperimentSerializerList(page, many=True)
            else:
                serializer = ExperimentSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                # add experiment membership
                experiment = AerpawExperiment.objects.get(pk=du.get('experiment_id'))
                is_experiment_creator = experiment.is_creator(request.user)
                is_experiment_member = experiment.is_member(request.user)
                response_data.append(
                    {
                        'canonical_number': du.get('canonical_number'),
                        'created_date': str(du.get('created_date')) if du.get('created_date') else None,
                        'description': du.get('description'),
                        'experiment_creator': du.get('experiment_creator'),
                        'experiment_id': du.get('experiment_id'),
                        'experiment_uuid': du.get('experiment_uuid'),
                        'is_canonical': du.get('is_canonical'),
                        'is_retired': du.get('is_retired'),
                        'membership': {
                            'is_experiment_creator': is_experiment_creator,
                            'is_experiment_member': is_experiment_member
                        },
                        'name': du.get('name'),
                        'project_id': du.get('project_id')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /experiments list")
            except PermissionDenied as exc:
                new_error(exc, request.user) 

    def create(self, request):
        """
        POST: create a new experiment (* = required fields)
        - canonical_number       - int
        - created_date           - string
        - description *          - string
        - experiment_creator     - int
        - experiment_id          - int
        - experiment_uuid        - string
        - experiment_membership  - array of user-experiment
        - experiment_state       - string
        - is_canonical           - boolean
        - is_retired             - boolean
        - name *                 - string
        - project_id *           - int
        - resources              - array of int

        Permission:
        - user is_experimenter AND
        - user is_project_creator OR
        - user is_project_member OR
        - user is_project_owner
        """
        try:
            project_id = request.data.get('project_id', None)
            if not project_id:
                try:
                    raise ValidationError(
                        detail="project_id: must provide project_id")
                except ValidationError as exc:
                    new_error(exc, request.user)
            project = get_object_or_404(AerpawProject.objects.all(), pk=int(project_id))
            user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        except ValidationError as exc:
            new_error(exc, request.user)
        if user.is_experimenter() and (project.is_creator(user) or project.is_member(user) or project.is_owner(user)):
            # validate description
            description = request.data.get('description', None)
            if not description or len(description) < EXPERIMENT_MIN_DESC_LEN:
                try:
                    raise ValidationError(
                        detail="description:  must be at least {0} chars long".format(EXPERIMENT_MIN_DESC_LEN))
                except ValidationError as exc:
                    new_error(exc, request.user)
            # validate name
            name = request.data.get('name', None)
            if not name or len(name) < EXPERIMENT_MIN_NAME_LEN:
                try:
                    raise ValidationError(
                        detail="name: must be at least {0} chars long".format(EXPERIMENT_MIN_NAME_LEN))
                except ValidationError as exc:
                    new_error(exc, request.user)
            # create experiment
            experiment = AerpawExperiment()
            experiment.created_by = user.username
            experiment.experiment_creator = user
            experiment.description = description
            experiment.modified_by = user.username
            experiment.name = name
            experiment.project = project
            experiment.uuid = uuid4()
            # set canonical_number
            canonical_number = CanonicalNumber()
            canonical_number.canonical_number = get_current_canonical_number()
            increment_current_canonical_number()
            canonical_number.save()
            experiment.canonical_number = canonical_number
            experiment.save()
            # set creator as experiment member
            membership = UserExperiment()
            membership.granted_by = user
            membership.experiment = experiment
            membership.user = user
            membership.save()
            return self.retrieve(request, pk=experiment.id)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to POST /experiments")
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve project as single result
        - canonical_number       - int
        - created_date           - string
        - description            - string
        - experiment_creator     - int
        - experiment_files       - array of experiment_files
        - experiment_flags       - string
        - experiment_id          - int
        - experiment_uuid        - string
        - experiment_members     - array of user-experiment
        - experiment_state       - string
        - is_canonical           - boolean
        - is_emulation_required  - boolean
        - is_retired             - boolean
        - name                   - string
        - project_id             - int
        - resources              - array of int
        - resources_locked       - boolean
        - members_locked         - boolean

        Permission:
        - user is_creator OR
        - user is_project_member OR
        - user is_project_owner OR
        - user is_operator
        """
        experiment = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        project = get_object_or_404(AerpawProject, pk=experiment.project.id)
        if project.is_creator(request.user) or project.is_member(request.user) or \
                project.is_owner(request.user) or request.user.is_operator():
            serializer = ExperimentSerializerDetail(experiment)
            du = dict(serializer.data)
            # add experiment_files
            linked_files = []
            if experiment.is_creator(request.user) or experiment.is_member(request.user) or request.user.is_operator():
                lf_serializer = ExperimentFileSerializerDetail(experiment.experiment_files, many=True)
                for f in lf_serializer.data:
                    df = dict(f)
                    linked_files.append(
                        {
                            'file_id': df.get('file_id'),
                            'file_location': df.get('file_location'),
                            'file_name': df.get('file_name'),
                            'file_notes': df.get('file_notes'),
                            'file_type': df.get('file_type'),
                            'is_active': df.get('is_active'),
                            'is_deleted': df.get('is_deleted')
                        }
                    )
            # add experiment membership
            is_experiment_creator = experiment.is_creator(request.user)
            is_experiment_member = experiment.is_member(request.user)
            experiment_membership = []
            for p in du.get('experiment_membership'):
                person = {
                    'granted_by': p.get('granted_by'),
                    'granted_date': str(p.get('granted_date')) if p.get('granted_date') else None,
                    'user_id': p.get('user_id')
                }
                experiment_membership.append(person)
            response_data = {
                'canonical_number': du.get('canonical_number'),
                'created_date': str(du.get('created_date')) if du.get('created_date') else None,
                'description': du.get('description'),
                'experiment_creator': du.get('experiment_creator'),
                'experiment_files': linked_files,
                'experiment_flags': du.get('experiment_flags'),
                'experiment_id': du.get('experiment_id'),
                'experiment_uuid': du.get('experiment_uuid'),
                'experiment_members': experiment_membership,
                'experiment_state': du.get('experiment_state'),
                'is_canonical': du.get('is_canonical'),
                'is_emulation_required': du.get('is_emulation_required'),
                'is_retired': du.get('is_retired'),
                'last_modified_by': AerpawUser.objects.get(username=du.get('last_modified_by')).id,
                'membership': {
                    'is_experiment_creator': is_experiment_creator,
                    'is_experiment_member': is_experiment_member
                },
                'modified_date': str(du.get('modified_date')) if du.get('modified_date') else None,
                'name': du.get('name'),
                'project_id': du.get('project_id'),
                'resources': du.get('resources'),
                'resources_locked': du.get('resources_locked'),
                'members_locked': du.get('members_locked')
            }
            if experiment.is_deleted:
                response_data['is_deleted'] = du.get('is_deleted')
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /experiments/{0} details".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def update(self, request, *args, **kwargs):
        """
        PUT: update an existing experiment
        - description            - string
        - is_retired             - boolean
        - name                   - string

        Permission:
        - user is_experiment_creator OR
        - user is_experiment_member
        """
        experiment = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if not experiment.is_deleted and \
                (request.user is experiment.experiment_creator or experiment.is_member(request.user)):
            if experiment.is_retired:
                try:
                    raise PermissionDenied(
                        detail="PermissionDenied: IS_RETIRED - unable to PUT/PATCH /experiments/{0} details".format(
                            kwargs.get('pk')))
                except PermissionDenied as exc:
                    new_error(exc, request.user)
            modified = False
            # check for description
            if request.data.get('description', None):
                if len(request.data.get('description')) < EXPERIMENT_MIN_DESC_LEN:
                    try:
                        raise ValidationError(
                            detail="description:  must be at least {0} chars long".format(EXPERIMENT_MIN_DESC_LEN))
                    except ValidationError as exc:
                        new_error(exc, request.user)
                experiment.description = request.data.get('description')
                modified = True
            # check for is_retired
            if str(request.data.get('is_retired')).casefold() in ['true', 'false']:
                is_retired = str(request.data.get('is_retired')).casefold() == 'true'
#                to_retired(request, experiment)	#Experimental
                experiment.is_retired = is_retired
                modified = True
            # check for name
            if request.data.get('name', None):
                if len(request.data.get('name')) < EXPERIMENT_MIN_NAME_LEN:
                    try:
                        raise ValidationError(
                            detail="name: must be at least {0} chars long".format(EXPERIMENT_MIN_NAME_LEN))
                    except ValidationError as exc:
                        new_error(exc, request.user)
                experiment.name = request.data.get('name')
                modified = True
            # save if modified
            if modified:
                experiment.modified_by = request.user.email
                experiment.save()
            return self.retrieve(request, pk=experiment.id)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to PUT/PATCH /experiments/{0} details".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update an existing experiment
        - description            - string
        - is_retired             - boolean
        - name                   - string

        Permission:
        - user is_experiment_creator OR
        - user is_experiment_member
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: soft delete existing project
        - is_deleted             - bool
        - is_retired             - bool

        Permission:
        - user is_experiment_creator OR
        - user is_experiment_member
        """
        experiment = get_object_or_404(self.queryset, pk=pk)
        if experiment.is_creator(request.user) or experiment.is_member(request.user):
            if experiment.is_retired:
                try:
                    raise PermissionDenied(
                        detail="PermissionDenied: IS_RETIRED - unable to DELETE /experiments/{0}".format(pk))
                except PermissionDenied as exc:
                    new_error(exc, request.user)
            experiment.is_deleted = True
            experiment.is_retired = True
            experiment.modified_by = request.user.username
            experiment.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            try: 
                raise PermissionDenied(
                    detail="PermissionDenied: unable to DELETE /experiments/{0}".format(pk))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    @action(detail=True, methods=['get', 'put', 'patch'])
    def resources(self, request, *args, **kwargs):
        """
        GET, PUT, PATCH: list / update experiment resources
        - resources  - array of resources

        Permission:
        - user is_experiment_creator OR
        - user is_experiment_member
        """
        experiment = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        if experiment.is_creator(request.user) or experiment.is_member(request.user) or request.user.is_operator():
            if str(request.method).casefold() in ['put', 'patch']:
                if request.data.get('experiment_resources') or isinstance(request.data.get('experiment_resources'),
                                                                          list):
                    if experiment.is_retired:
                        try:
                            raise PermissionDenied(
                                detail="PermissionDenied: IS_RETIRED - unable to GET,PUT,PATCH /experiments/{0}/resources".format(
                                    kwargs.get('pk')))
                        except PermissionDenied as exc:
                            new_error(exc, request.user)
                    if experiment.resources_locked:
                        try:
                            raise PermissionDenied(
                                detail="PermissionDenied: RESOURCES_LOCKED - unable to PUT,PATCH /experiments/{0}/resources".format(
                                    kwargs.get('pk')))
                        except PermissionDenied as exc:
                            new_error(exc, request.user)
                    resource_ids = request.data.get('experiment_resources')
                    if isinstance(resource_ids, list) and all([isinstance(item, int) for item in resource_ids]):
                        resources_orig = list(set(experiment.resources.all().values_list('id', flat=True)))
                        resources_added = list(set(resource_ids).difference(set(resources_orig)))
                        resources_removed = list(set(resources_orig).difference(set(resource_ids)))
                        # TODO: canonical-experiment-resource logic
                        print(f'resources_added: {resources_added}')
                        for pk in resources_added:
                            if AerpawResource.objects.filter(pk=pk).exists():
                                resource = AerpawResource.objects.get(pk=pk)
                                if not experiment.is_canonical or \
                                        (experiment.is_canonical and
                                         resource.resource_class == AerpawResource.ResourceClass.ALLOW_CANONICAL):
                                    # add resource to project
                                    experiment.resources.add(resource)
                                    # create canonical-experiment-resource if resource is_canonical
                                    canonical_experiment_resource = CanonicalExperimentResource()
                                    canonical_experiment_resource.experiment = experiment
                                    canonical_experiment_resource.resource = resource
                                    canonical_experiment_resource.node_display_name = resource.name
                                    canonical_experiment_resource.node_uhd = CanonicalExperimentResource.NodeUhd.FOUR_THREE
                                    if resource.resource_type == AerpawResource.ResourceType.AFRN:
                                        canonical_experiment_resource.node_type = CanonicalExperimentResource.NodeType.AFRN
                                        canonical_experiment_resource.node_vehicle = CanonicalExperimentResource.NodeVehicle.VEHICLE_NONE
                                    elif resource.resource_type == AerpawResource.ResourceType.APRN:
                                        canonical_experiment_resource.node_type = CanonicalExperimentResource.NodeType.APRN
                                        if resource.resource_type == AerpawResource.ResourceType.UAV:
                                            canonical_experiment_resource.node_vehicle = CanonicalExperimentResource.NodeVehicle.VEHICLE_UAV
                                        if resource.resource_type == AerpawResource.ResourceType.UGV:
                                            canonical_experiment_resource.node_vehicle = CanonicalExperimentResource.NodeVehicle.VEHICLE_UGV
                                        if resource.resource_type == AerpawResource.ResourceType.OTHER:
                                            canonical_experiment_resource.node_vehicle = CanonicalExperimentResource.NodeVehicle.VEHICLE_OTHER
                                        if resource.resource_type == AerpawResource.ResourceType.THREE_PBBE:
                                            canonical_experiment_resource.node_vehicle = CanonicalExperimentResource.NodeVehicle.VEHICLE_NONE
                                    elif resource.resource_type == AerpawResource.ResourceType.ACN:
                                        canonical_experiment_resource.node_type == CanonicalExperimentResource.NodeType.ACN
                                        canonical_experiment_resource.node_vehicle = CanonicalExperimentResource.NodeVehicle.VEHICLE_NONE
                                    canonical_experiment_resource.save()
                                else:
                                    try:
                                        raise ValidationError(
                                            detail="ValidationError: ALLOW_CANONICAL /experiments/{0}/resources".format(
                                                kwargs.get('pk')))
                                    except ValidationError as exc:
                                        new_error(exc, request.user)

                        for pk in resources_removed:
                            resource = AerpawResource.objects.get(pk=pk)
                            # remove/delete canonical-experiment-resource if resource is_canonical
                            canonical_experiment_resource = CanonicalExperimentResource.objects.filter(
                                resource__id=pk,
                                experiment__id=experiment.id
                            )
                            canonical_experiment_resource.delete()
                            # remove resource from project
                            experiment.resources.remove(resource)
                            experiment.save()
                    # calculate experiment node numbers
                    cers = CanonicalExperimentResource.objects.filter(experiment__id=experiment.id).order_by(
                        'created')
                    if isinstance(request.data.get('node_numbers'), list):
                        node_numbers = {int(resource_node_number.split('-')[0]): int(resource_node_number.split('-')[1]) for resource_node_number in request.data.get('node_numbers')}
                        print(f'node_numbers: {node_numbers}')
                        for cer in cers:
                            cer.experiment_node_number = node_numbers[cer.resource.id]
                            cer.save()
                    else:
                        enn = 1
                        for cer in cers:
                            cer.experiment_node_number = enn
                            cer.save()
                            enn += 1
                else:
                    try:
                        raise ValidationError(
                            detail="ValidationError: invalid resource_id or node_uhd /experiments/{0}/resources".format(
                                kwargs.get('pk')))
                    except ValidationError as exc:
                        new_error(exc, request.user)
                experiment.save()
            # End of PUT, PATCH section - All reqeust types return resources
            serializer = ResourceSerializerDetail(experiment.resources, many=True)
            resources = []
            for u in serializer.data:
                du = dict(u)
                resources.append(
                    {
                        'description': du.get('description'),
                        'is_active': du.get('is_active'),
                        'location': du.get('location'),
                        'name': du.get('name'),
                        'resource_class': du.get('resource_class'),
                        'resource_id': du.get('resource_id'),
                        'resource_mode': du.get('resource_mode'),
                        'resource_type': du.get('resource_type')
                    }
                )
            response_data = {'experiment_resources': resources}
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET,PUT,PATCH /experiments/{0}/resources".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    @action(detail=True, methods=['get', 'put', 'patch'])
    def membership(self, request, *args, **kwargs):
        """
        GET, PUT, PATCH: list / update experiment members
        - experiment_members     - array of user-experiment

        Permission:
        - user is_experiment_creator OR
        - user is_experiment_member
        """
        experiment = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        if experiment.is_creator(request.user) or experiment.is_member(request.user) or request.user.is_operator():
            if str(request.method).casefold() in ['put', 'patch', 'post']:
                if request.data.get('experiment_members') or isinstance(request.data.get('experiment_members'), list):
                    if experiment.is_retired:
                        try:
                            raise PermissionDenied(
                                detail="PermissionDenied: IS_RETIRED - unable to GET,PUT,PATCH /experiments/{0}/membership".format(
                                    kwargs.get('pk')))
                        except PermissionDenied as exc:
                            new_error(exc, request.user)
                    experiment_members = request.data.get('experiment_members')
                    if isinstance(experiment_members, list) and all(
                            [isinstance(item, int) for item in experiment_members]):
                        experiment_members_orig = UserExperiment.objects.filter(
                            experiment__id=experiment.id
                        ).values_list('user__id', flat=True)
                        experiment_members_added = list(
                            set(experiment_members).difference(set(experiment_members_orig)))
                        experiment_members_removed = list(
                            set(experiment_members_orig).difference(set(experiment_members)))
                        for pk in experiment_members_added:
                            if AerpawUser.objects.filter(pk=pk).exists():
                                user = AerpawUser.objects.get(pk=pk)
                                # limited to project membership (project_member, project_owner)
                                if experiment.project.is_member(user) or experiment.project.is_owner(user):
                                    membership = UserExperiment()
                                    membership.granted_by = request.user
                                    membership.experiment = experiment
                                    membership.user = user
                                    membership.save()
                        # add experiment members message
                        generate_user_messages_from_experiment_membership(
                            request=request, experiment=experiment, experiment_members=experiment_members_added,
                            add=True)
                        for pk in experiment_members_removed:
                            membership = UserExperiment.objects.get(
                                experiment__id=experiment.id, user__id=pk)
                            membership.delete()
                        # remove experiment members message
                        generate_user_messages_from_experiment_membership(
                            request=request, experiment=experiment, experiment_members=experiment_members_removed,
                            add=False)
            # End of PUT, PATCH section - All reqeust types return membership
            serializer = ExperimentSerializerDetail(experiment)
            du = dict(serializer.data)
            experiment_membership = []
            for p in du.get('experiment_membership'):
                person = {
                    'granted_by': p.get('granted_by'),
                    'granted_date': str(p.get('granted_date')),
                    'user_id': p.get('user_id')
                }
                experiment_membership.append(person)
            response_data = {
                'experiment_members': experiment_membership
            }
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET,PUT,PATCH /experiments/{0}/membership".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    @action(detail=True, methods=['get', 'put', 'patch'])
    def state(self, request, *args, **kwargs):
        """
        GET, PUT, PATCH: retrieve / update experiment state
        - experiment_state     - string

        Permission:
        - user is_experiment_creator OR
        - user is_experiment_member OR
        - user is_operator
        """
        experiment = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        # check if experiment is retired
        if experiment.is_retired:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: IS_RETIRED - unable to GET,PUT,PATCH /experiments/{0}/state".format(
                        kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)
        # check if user is experimenter or operator
        if experiment.is_creator(request.user) or experiment.is_member(request.user) or request.user.is_operator():
            if str(request.method).casefold() in ['put', 'patch']:
                # check for state transition request
                next_state = request.data.get('next_state', experiment.state())
                if is_valid_transition(experiment=experiment, next_state=next_state, user=request.user):
                    transition_experiment_state(request=request, experiment=experiment, next_state=next_state)
                else:
                    try:
                        raise ValidationError(
                            detail="ValidationError: invalid role or transition '{0}' --> '{1}' for /experiments/{2}/state".format(
                                experiment.state(), next_state, kwargs.get('pk')))
                    except ValidationError as exc:
                        new_error(exc, request.user)
            # End of PUT, PATCH section - All reqeust types return experiment state
            serializer = ExperimentSerializerState(experiment)
            du = dict(serializer.data)
            response_data = {
                'experiment_flags': du.get('experiment_flags'),
                'experiment_id': du.get('experiment_id'),
                'experiment_state': du.get('experiment_state'),
                'experiment_uuid': du.get('experiment_uuid')
            }
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET,PUT,PATCH /experiments/{0}/state".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    @action(detail=True, methods=['get', 'put', 'patch'])
    def files(self, request, *args, **kwargs):
        """
        GET, PUT, PATCH: list / update experiment files
        - experiment_files     - array of linked files

        Permission:
        - user is_experiment_creator OR
        - user is_experiment_member OR
        - user is_operator
        """
        experiment = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        if experiment.is_creator(request.user) or experiment.is_member(request.user) or request.user.is_operator():
            if str(request.method).casefold() in ['put', 'patch']:
                if request.data.get('experiment_files') or isinstance(request.data.get('experiment_files'), list):
                    if experiment.is_retired:
                        try:
                            raise PermissionDenied(
                                detail="PermissionDenied: IS_RETIRED - unable to GET,PUT,PATCH /experiments/{0}/files".format(
                                    kwargs.get('pk')))
                        except PermissionDenied as exc:
                            new_error(exc, request.user)
                    experiment_files = request.data.get('experiment_files')
                    if isinstance(experiment_files, list) and all(
                            [isinstance(item, int) for item in experiment_files]):
                        experiment_files_orig = [lf.id for lf in experiment.experiment_files.all()]
                        experiment_files_added = list(
                            set(experiment_files).difference(set(experiment_files_orig)))
                        experiment_files_removed = list(
                            set(experiment_files_orig).difference(set(experiment_files)))
                        for pk in experiment_files_added:
                            if ExperimentFile.objects.filter(pk=pk).exists():
                                linked_file = ExperimentFile.objects.get(pk=pk)
                                # limited to operator
                                if request.user.is_operator and not linked_file.is_deleted:
                                    experiment.experiment_files.add(linked_file)
                                    experiment.save()
                                else:
                                    try:
                                        raise PermissionDenied(
                                            detail="PermissionDenied: non-operator or deleted file - unable to PUT,PATCH /experiments/{0}/files - file_id: {1}".format(
                                                kwargs.get('pk'), pk))
                                    except PermissionDenied as exc:
                                        new_error(exc, request.user)
                            else:
                                try:
                                    raise NotFound(
                                        detail="NotFound: unable to PUT,PATCH /experiments/{0}/files - file_id: {1}".format(
                                            kwargs.get('pk'), pk))
                                except NotFound as exc:
                                    new_error(exc, request.user)
                        for pk in experiment_files_removed:
                            # limited to operator
                            if request.user.is_operator:
                                linked_file = ExperimentFile.objects.get(pk=pk)
                                experiment.experiment_files.remove(linked_file)
                                experiment.save()
                            else:
                                try:
                                    raise PermissionDenied(
                                        detail="PermissionDenied: non-operator - unable to PUT,PATCH /experiments/{0}/files - file_id: {1}".format(
                                            kwargs.get('pk'), pk))
                                except PermissionDenied as exc:
                                    new_error(exc, request.user)
                        # End of PUT, PATCH section - All reqeust types return linked files
            serializer = ExperimentFileSerializerDetail(experiment.experiment_files, many=True)
            experiment_files = []
            for u in serializer.data:
                du = dict(u)
                experiment_files.append(
                    {
                        'file_id': du.get('file_id'),
                        'file_location': du.get('file_location'),
                        'file_name': du.get('file_name'),
                        'file_notes': du.get('file_notes'),
                        'file_type': du.get('file_type'),
                        'is_deleted': du.get('is_deleted')
                    }
                )
            response_data = {'experiment_files': experiment_files}
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET,PUT,PATCH /experiments/{0}/files".format(
                        kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    @action(detail=True, methods=['get', 'put', 'patch'])
    def sessions(self, request, *args, **kwargs):
        """
        GET: list experiment sessions
        - experiment_sessions     - array of sessions

        Permission:
        - user is_experiment_creator OR
        - user is_experiment_member OR
        - user is_operator
        """
        experiment = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        if experiment.is_creator(request.user) or experiment.is_member(request.user) or request.user.is_operator():
            sessions = OnDemandSession.objects.filter(experiment_id=experiment.id).order_by('-created')
            serializer = OnDemandSessionSerializerDetail(sessions, many=True)
            experiment_sessions = []
            for u in serializer.data:
                du = dict(u)
                try:
                    created_by = AerpawUser.objects.get(username=du.get('created_by')).id
                except Exception as exc:
                    print(exc)
                    new_error(exc, request.user)
                    created_by = None
                try:
                    modified_by = AerpawUser.objects.get(username=du.get('modified_by')).id
                except Exception as exc:
                    print(exc)
                    new_error(exc, request.user)
                    modified_by = None
                experiment_sessions.append(
                    {
                        'created_by': created_by,
                        'created_time': str(du.get('created_time')) if du.get('created_time') else None,
                        'end_date_time': str(du.get('end_date_time')) if du.get('end_date_time') else None,
                        'ended_by': du.get('ended_by'),
                        'experiment_id': du.get('experiment_id'),
                        'is_active': du.get('is_active'),
                        'modified_by': modified_by,
                        'modified_time': str(du.get('modified_time')) if du.get('modified_time') else None,
                        'session_id': du.get('session_id'),
                        'session_type': du.get('session_type'),
                        'start_date_time': str(du.get('start_date_time')) if du.get('start_date_time') else None,
                        'started_by': du.get('started_by')
                    }
                )
            response_data = {'experiment_sessions': experiment_sessions}
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET,PUT,PATCH /experiments/{0}/sessions".format(
                        kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)


class UserExperimentViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    User Experiment
    - paginated list
    - retrieve one
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserExperiment.objects.all().order_by('-granted_date').distinct()
    serializer_class = UserExperimentSerializer

    def get_queryset(self):
        experiment_id = self.request.query_params.get('experiment_id', None)
        user_id = self.request.query_params.get('user_id', None)
        if experiment_id and user_id:
            queryset = UserExperiment.objects.filter(
                experiment__id=experiment_id,
                user__id=user_id
            ).order_by('-granted_date').distinct()
        elif experiment_id:
            queryset = UserExperiment.objects.filter(
                experiment__id=experiment_id
            ).order_by('-granted_date').distinct()
        elif user_id:
            queryset = UserExperiment.objects.filter(
                user__id=user_id
            ).order_by('-granted_date').distinct()
        else:
            queryset = UserExperiment.objects.filter().order_by('-granted_date').distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list user-experiment as paginated results
        - experiment_id          - int
        - granted_by             - int
        - granted_date           - string
        - id                     - int
        - user_id                - int

        Permission:
        - user is_operator
        """
        if request.user.is_operator():
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = UserExperimentSerializer(page, many=True)
            else:
                serializer = UserExperimentSerializer(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'experiment_id': du.get('experiment_id'),
                        'granted_by': du.get('granted_by'),
                        'granted_date': str(du.get('granted_date')) if du.get('granted_date') else None,
                        'id': du.get('id'),
                        'user_id': du.get('user_id')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /user-experiment list")
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def create(self, request):
        """
        POST: user-experiment cannot be created via the API
        """
        try:
            raise MethodNotAllowed(method="POST: /user-experiment")
        except MethodNotAllowed as exc:
            new_error(exc, request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        GET: user-experiment as detailed result
        - experiment_id          - int
        - granted_by             - int
        - granted_date           - string
        - id                     - int
        - user_id                - int

        Permission:
        - user is_operator
        """
        user_experiment = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_operator():
            serializer = UserExperimentSerializer(user_experiment)
            du = dict(serializer.data)
            response_data = {
                'experiment_id': du.get('experiment_id'),
                'granted_by': du.get('granted_by'),
                'granted_date': str(du.get('granted_date')) if du.get('granted_date') else None,
                'id': du.get('id'),
                'user_id': du.get('user_id')
            }
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /user-experiment/{0} details".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def update(self, request, *args, **kwargs):
        """
        PUT: user-experiment cannot be updated via the API
        """
        raise MethodNotAllowed(method="PUT/PATCH: /user-experiment/{int:pk}")

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: user-experiment cannot be updated via the API
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: user-experiment cannot be deleted via the API
        """
        raise MethodNotAllowed(method="DELETE: /user-experiment/{int:pk}")


class OnDemandSessionViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Experiment Session
    - paginated list
    - retrieve one
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = OnDemandSession.objects.all().order_by('-created').distinct()
    serializer_class = OnDemandSessionSerializerDetail

    def get_queryset(self):
        experiment_id = self.request.query_params.get('experiment_id', None)
        active = self.request.query_params.get('active', None)
        if active and str(active).casefold() == 'true':
            active_set = [True]
        elif active and str(active).casefold() == 'false':
            active_set = [False]
        else:
            active_set = [True, False]
        if experiment_id:
            queryset = OnDemandSession.objects.filter(
                experiment__id=experiment_id,
                is_active__in=active_set
            ).order_by('-created').distinct()
        else:
            queryset = OnDemandSession.objects.filter(
                is_active__in=active_set
            ).order_by('-created').distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list experiment-session as paginated results
        - created_by (fk)        - int
        - end_date_time          - string
        - ended_by (fk)          - user_id
        - experiment_id (fk)     - int
        - is_active              - bool
        - session_id (pk)        - int
        - session_type           - string
        - start_date_time        - string
        - started_by (fk)        - user_id

        Permission:
        - user is_operator
        - user is_experiment_creator
        - user is_experiment_member
        """
        try:
            experiment = AerpawExperiment.objects.get(pk=request.query_params.get('experiment_id'))
            is_experiment_creator = experiment.is_creator(request.user)
            is_experiment_member = experiment.is_member(request.user)
        except Exception as exc:
            is_experiment_creator = False
            is_experiment_member = False

        if request.user.is_operator() or is_experiment_creator or is_experiment_member:
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = OnDemandSessionSerializerList(page, many=True)
            else:
                serializer = OnDemandSessionSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'end_date_time': str(du.get('end_date_time')) if du.get('end_date_time') else None,
                        'ended_by': du.get('ended_by'),
                        'experiment_id': du.get('experiment_id'),
                        'is_active': du.get('is_active'),
                        'session_id': du.get('session_id'),
                        'session_type': du.get('session_type'),
                        'start_date_time': str(du.get('start_date_time')) if du.get('start_date_time') else None,
                        'started_by': du.get('started_by')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /experiment-session list")
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def create(self, request):
        """
        POST: create a new experiment-session
        - created_by (fk)        - int
        - created_time           - string
        - end_date_time          - string
        - ended_by (fk)          - user_id
        - experiment_id (fk)     - int
        - modified_by (fk)       - int
        - modified_time          - string
        - session_id (pk)        - int
        - session_type           - string
        - start_date_time        - string
        - started_by (fk)        - user_id
        - uuid                   - string

        Permission:
        - user is_operator
        """
        raise MethodNotAllowed(method="POST: /experiment-session")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve experiment-session as detailed result
        - created_by (fk)        - int
        - end_date_time          - string
        - ended_by (fk)          - user_id
        - experiment_id (fk)     - int
        - is_active              - bool
        - session_id (pk)        - int
        - session_type           - string
        - start_date_time        - string
        - started_by (fk)        - user_id

        Permission:
        - user is_operator
        - user is_experiment_creator
        - user is_experiment_member
        """
        experiment_session = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        try:
            experiment = AerpawExperiment.objects.get(pk=experiment_session.experiment_id)
            is_experiment_creator = experiment.is_creator(request.user)
            is_experiment_member = experiment.is_member(request.user)
        except Exception as exc:
            new_error(exc, request.user)
            is_experiment_creator = False
            is_experiment_member = False

        if request.user.is_operator() or is_experiment_creator or is_experiment_member:
            serializer = OnDemandSessionSerializerDetail(experiment_session)
            du = dict(serializer.data)
            try:
                created_by = AerpawUser.objects.get(username=du.get('created_by')).id
            except Exception as exc:
                new_error(exc, request.user)
                created_by = None
            try:
                modified_by = AerpawUser.objects.get(username=du.get('modified_by')).id
            except Exception as exc:
                new_error(exc, request.user)
                modified_by = None
            response_data = {
                'created_by': created_by,
                'created_time': str(du.get('created_time')) if du.get('created_time') else None,
                'end_date_time': str(du.get('end_date_time')) if du.get('end_date_time') else None,
                'ended_by': du.get('ended_by'),
                'experiment_id': du.get('experiment_id'),
                'is_active': du.get('is_active'),
                'modified_by': modified_by,
                'modified_time': str(du.get('modified_time')) if du.get('modified_time') else None,
                'session_id': du.get('session_id'),
                'session_type': du.get('session_type'),
                'start_date_time': str(du.get('start_date_time')) if du.get('start_date_time') else None,
                'started_by': du.get('started_by')
            }
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /experiment-session/{0} details".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def update(self, request, *args, **kwargs):
        """
        PUT: update an existing experiment-session
        - end_date_time          - string
        - ended_by (fk)          - user_id
        - experiment_id (fk)     - int
        - session_id (pk)        - int
        - session_type           - string
        - start_date_time        - string
        - started_by (fk)        - user_id

        Permission:
        - user is_operator
        """
        raise MethodNotAllowed(method="PUT/PATCH: /experiment-session/{int:pk}")

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update an existing experiment-session
        - end_date_time          - string
        - ended_by (fk)          - user_id
        - experiment_id (fk)     - int
        - session_id (pk)        - int
        - session_type           - string
        - start_date_time        - string
        - started_by (fk)        - user_id

        Permission:
        - user is_operator
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: remove an existing experiment-session
        - end_date_time          - string
        - ended_by (fk)          - user_id
        - experiment_id (fk)     - int
        - session_id (pk)        - int
        - session_type           - string
        - start_date_time        - string
        - started_by (fk)        - user_id

        Permission:
        - user is_operator
        """
        raise MethodNotAllowed(method="DELETE: /experiment-session/{int:pk}")

class ScheduledSessionViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Experiment Session
    - paginated list
    - retrieve one
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = ScheduledSession.objects.all().order_by('-created').distinct()
    serializer_class = ScheduledSessionSerializerDetail

    def get_queryset(self):
        experiment_id = self.request.query_params.get('experiment_id', None)
        active = self.request.query_params.get('active', None)
        if active and str(active).casefold() == 'true':
            active_set = [True]
        elif active and str(active).casefold() == 'false':
            active_set = [False]
        else:
            active_set = [True, False]
        if experiment_id:
            queryset = ScheduledSession.objects.filter(
                experiment__id=experiment_id,
                is_active__in=active_set
            ).order_by('-created').distinct()
        else:
            queryset = ScheduledSession.objects.filter(
                is_active__in=active_set
            ).order_by('-created').distinct()
        return queryset
    
    def list(self, request,  *args, **kwargs):
        print(f'ScheduledSessionViewSet sessions self = {self}')
        try:
            experiment = AerpawExperiment.objects.get(pk=request.query_params.get('experiment_id'))
            is_experiment_creator = experiment.is_creator(request.user)
            is_experiment_member = experiment.is_member(request.user)
        except Exception as exc:
            new_error(exc, request.user)
            is_experiment_creator = False
            is_experiment_member = False

        if request.user.is_operator() or is_experiment_creator or is_experiment_member:
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = ScheduledSessionSerializerList(page, many=True)
            else:
                serializer = ScheduledSessionSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'end_date_time': str(du.get('end_date_time')) if du.get('end_date_time') else None,
                        'ended_by': du.get('ended_by'),
                        'experiment_id': du.get('experiment_id'),
                        'is_active': du.get('is_active'),
                        'scheduled_start':du.get('scheduled_start'),
                        'scheduled_end':du.get('scheduled_end'),
                        'session_id': du.get('session_id'),
                        'session_type': du.get('session_type'),
                        'start_date_time': str(du.get('start_date_time')) if du.get('start_date_time') else None,
                        'started_by': du.get('started_by')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /experiment-session list")
            except PermissionDenied as exc:
                new_error(exc, request.user)
        
    def sessions_list(self, request,  *args, **kwargs):
        try:
            experiment = AerpawExperiment.objects.get(pk=request.query_params.get('experiment_id'))
            is_experiment_creator = experiment.is_creator(request.user)
            is_experiment_member = experiment.is_member(request.user)
        except Exception as exc:
            new_error(exc, request.user)
            is_experiment_creator = False
            is_experiment_member = False

        if request.user.is_operator() or is_experiment_creator or is_experiment_member:
            # Reomves non-ops sessions if they have an ops session. 
            ops_session_ids = [session.id for session in kwargs['ops_sessions']]
            print(ops_session_ids)
            sessions = [session for session in kwargs['sessions'] if session.id not in ops_session_ids]
            print(sessions)
            sessions_queryset = list(chain(kwargs['ops_sessions'], sessions))
            print(sessions_queryset)
            page = self.paginate_queryset(sessions_queryset)
            if page:
                serializer = ScheduledSessionSerializerList(page, many=True)
            else:
                serializer = ScheduledSessionSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'end_date_time': str(du.get('end_date_time')) if du.get('end_date_time') else None,
                        'ended_by': du.get('ended_by'),
                        'experiment_id': du.get('experiment_id'),
                        'is_active': du.get('is_active'),
                        'scheduled_start':du.get('scheduled_start'),
                        'scheduled_end':du.get('scheduled_end'),
                        'session_id': du.get('session_id'),
                        'session_state': du.get('session_state') if du.get('session_state') else None,
                        'session_type': du.get('session_type'),
                        'start_date_time': str(du.get('start_date_time')) if du.get('start_date_time') else None,
                        'started_by': du.get('started_by')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /experiment-session list")
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve scheduled-session as detailed result
        - created_by (fk)        - int
        - description            - string
        - end_date_time          - string
        - ended_by (fk)          - user_id
        - experiment_id (fk)     - int
        - is_active              - bool
        - scheduled_start        - string
        - scheduled_end          - string
        - session_id (pk)        - int
        - session_type           - string
        - start_date_time        - string
        - started_by (fk)        - user_id

        Permission:
        - user is_operator
        - user is_experiment_creator
        - user is_experiment_member
        """
        scheduled_session = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        try:
            experiment = AerpawExperiment.objects.get(pk=scheduled_session.experiment_id)
            is_experiment_creator = experiment.is_creator(request.user)
            is_experiment_member = experiment.is_member(request.user)
        except Exception as exc:
            new_error(exc, request.user)
            is_experiment_creator = False
            is_experiment_member = False

        if request.user.is_operator() or is_experiment_creator or is_experiment_member:
            serializer = ScheduledSessionSerializerDetail(scheduled_session)
            du = dict(serializer.data)
            try:
                created_by = AerpawUser.objects.get(username=du.get('created_by')).id
            except Exception as exc:
                new_error(exc, request.user)
                created_by = None
            try:
                modified_by = AerpawUser.objects.get(username=du.get('modified_by')).id
            except Exception as exc:
                new_error(exc, request.user)
                modified_by = None
            response_data = {
                'created_by': created_by,
                'created_time': str(du.get('created_time')) if du.get('created_time') else None,
                'description': du.get('description') if du.get('description') else None,
                'end_date_time': str(du.get('end_date_time')) if du.get('end_date_time') else None,
                'ended_by': du.get('ended_by'),
                'experiment_id': du.get('experiment_id'),
                'is_active': du.get('is_active'),
                'modified_by': modified_by,
                'modified_time': str(du.get('modified_time')) if du.get('modified_time') else None,
                'scheduled_start': str(du.get('scheduled_start')) if du.get('scheduled_start') else None,
                'scheduled_end': str(du.get('scheduled_end')) if du.get('scheduled_end') else None,
                'session_id': du.get('session_id'),
                'session_type': du.get('session_type'),
                'start_date_time': str(du.get('start_date_time')) if du.get('start_date_time') else None,
                'started_by': du.get('started_by')
            }
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /experiment-session/{0} details".format(kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)
            return None


class CanonicalExperimentResourceViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Experiment Session
    - paginated list
    - retrieve one
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = CanonicalExperimentResource.objects.all().order_by('-created').distinct()
    serializer_class = CanonicalExperimentResourceSerializer

    def get_queryset(self):
        experiment_id = self.request.query_params.get('experiment_id', None)
        resource_id = self.request.query_params.get('resource_id', None)
        if experiment_id and resource_id:
            queryset = CanonicalExperimentResource.objects.filter(
                experiment__id=experiment_id,
                resource__id=resource_id
            ).order_by('experiment_node_number').distinct()
        elif experiment_id:
            queryset = CanonicalExperimentResource.objects.filter(
                experiment__id=experiment_id
            ).order_by('experiment_node_number').distinct()
        elif resource_id:
            queryset = CanonicalExperimentResource.objects.filter(
                resource__id=resource_id
            ).order_by('experiment_node_number').distinct()
        else:
            queryset = CanonicalExperimentResource.objects.filter().order_by('experiment_node_number').distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list canonical-experiment-resource as paginated results
        - canonical_experiment_resource_id - int
        - experiment_id (fk)               - int
        - experiment_node_number           - int
        - node_type                        - string
        - node_uhd                         - string
        - node_vehicle                     - string
        - resource_id (fk)                 - int

        Permission:
        - user is_operator
        """
        try:
            experiment_id = self.request.query_params.get('experiment_id', None)
            experiment = AerpawExperiment.objects.get(pk=experiment_id)
            if experiment.is_creator(request.user) or experiment.is_member(request.user):
                is_experimenter = True
            else:
                is_experimenter = False
        except Exception as exc:
            print(exc)
            new_error(exc, request.user)
            is_experimenter = False
        if request.user.is_operator() or is_experimenter:
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = CanonicalExperimentResourceSerializer(page, many=True)
            else:
                serializer = CanonicalExperimentResourceSerializer(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                if du.get('node_type') == CanonicalExperimentResource.NodeType.APRN.value:
                    resource_id = None
                else:
                    resource_id = du.get('resource_id')
                response_data.append(
                    {
                        'canonical_experiment_resource_id': du.get('canonical_experiment_resource_id'),
                        'experiment_id': du.get('experiment_id'),
                        'experiment_node_number': du.get('experiment_node_number'),
                        'node_display_name': du.get('node_display_name'),
                        'node_type': du.get('node_type'),
                        'node_uhd': du.get('node_uhd'),
                        'node_vehicle': du.get('node_vehicle'),
                        'resource_id': resource_id,
                        'resource_hostname': du.get('resource_hostname'),
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /canonical-experiment-resource list")
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def create(self, request):
        """
        POST: create a new canonical-experiment-resource
        - experiment_id (fk)      - int
        - experiment_node_number  - int
        - node_type               - string
        - node_uhd                - string
        - node_vehicle            - string
        - resource_id (fk)        - int

        Permission:
        - user is_operator
        """
        raise MethodNotAllowed(method="POST: /canonical-experiment-resource")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve canonical-experiment-resource as detailed result
        - canonical_experiment_resource_id - int
        - experiment_id (fk)               - int
        - experiment_node_number           - int
        - node_type                        - string
        - node_uhd                         - string
        - node_vehicle                     - string
        - resource_id (fk)                 - int

        Permission:
        - user is_operator
        """
        canonical_experiment_resource = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        try:
            experiment_id = canonical_experiment_resource.experiment.id
            experiment = AerpawExperiment.objects.get(pk=experiment_id)
            if experiment.is_creator(request.user) or experiment.is_member(request.user):
                is_experimenter = True
            else:
                is_experimenter = False
        except Exception as exc:
            print(exc)
            new_error(exc, request.user)
            is_experimenter = False
        if request.user.is_operator() or is_experimenter:
            serializer = CanonicalExperimentResourceSerializer(canonical_experiment_resource)
            du = dict(serializer.data)
            response_data = {
                'canonical_experiment_resource_id': du.get('canonical_experiment_resource_id'),
                'experiment_id': du.get('experiment_id'),
                'experiment_node_number': du.get('experiment_node_number'),
                'node_display_name': du.get('node_display_name'),
                'node_type': du.get('node_type'),
                'node_uhd': du.get('node_uhd'),
                'node_vehicle': du.get('node_vehicle'),
                'resource_id': du.get('resource_id')
            }
            return Response(response_data)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to GET /canonical-experiment-resource/{0} details".format(
                        kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def update(self, request, *args, **kwargs):
        """
        PUT: update an existing canonical-experiment-resource
        - experiment_id (fk)      - int
        - experiment_node_number  - int
        - node_display_name       - string
        - node_type               - string
        - node_uhd                - string
        - node_vehicle            - string
        - resource_id (fk)        - int

        Permission:
        - user is_operator
        """
        cer = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if cer.experiment.is_creator(request.user) or cer.experiment.is_member(request.user):
            if cer.experiment.is_retired:
                try:
                    raise PermissionDenied(
                        detail="PermissionDenied: IS_RETIRED - unable to PUT/PATCH /canonical-experiment-resource/{0} details".format(
                            kwargs.get('pk')))
                except PermissionDenied as exc:
                    new_error(exc, request.user)
            modified = False
            # check node_display_name
            if request.data.get('node_display_name', None):
                cer.node_display_name = request.data.get('node_display_name')
                modified = True
            # check node_uhd
            if request.data.get('node_uhd', None):
                if request.data.get('node_uhd') not in [c[0] for c in CanonicalExperimentResource.NodeUhd.choices]:
                    try:
                        raise ValidationError(
                            detail="node_uhd:  valid choices are {0}".format(
                                [c[0] for c in CanonicalExperimentResource.NodeUhd.choices]))
                    except ValidationError as exc:
                        new_error(exc, request.user)
                cer.node_uhd = request.data.get('node_uhd')
                modified = True
            # check node_vehicle
            if request.data.get('node_vehicle', None):
                node_vehicle = request.data.get('node_vehicle')
                if node_vehicle not in [c[0] for c in CanonicalExperimentResource.NodeVehicle.choices]:
                    try:
                        raise ValidationError(
                            detail="node_vehicle:  valid choices are {0}".format(
                                [c[0] for c in CanonicalExperimentResource.NodeVehicle.choices]))
                    except ValidationError as exc:
                        new_error(exc, request.user)
                # AFRN must be vehicle_none
                if cer.resource.resource_type == AerpawResource.ResourceType.AFRN and node_vehicle != CanonicalExperimentResource.NodeVehicle.VEHICLE_NONE:
                    try:
                        raise ValidationError(
                            detail="node_vehicle: resource type AFRN must be vehicle_none")
                    except ValidationError as exc:
                        new_error(exc, request.user)
                # APRN must be in [vehicle_uav, vehicle_ugv, vehicle_none]
                if cer.resource.resource_type == AerpawResource.ResourceType.APRN and node_vehicle not in [
                    CanonicalExperimentResource.NodeVehicle.VEHICLE_UAV,
                    CanonicalExperimentResource.NodeVehicle.VEHICLE_UGV,
                    CanonicalExperimentResource.NodeVehicle.VEHICLE_NONE]:
                    try:
                        raise ValidationError(
                            detail="node_vehicle: resource type APRN must be in [vehicle_uav, vehicle_ugv, vehicle_none]")
                    except ValidationError as exc:
                        new_error(exc, request.user)
                # TODO: other checks for UAV, UGV, 3PBBE, Other
                cer.node_vehicle = request.data.get('node_vehicle')
                modified = True
            # save if modified
            if modified:
                cer.modified_by = request.user.email
                cer.save()
            return self.retrieve(request, pk=cer.id)
        else:
            try:
                raise PermissionDenied(
                    detail="PermissionDenied: unable to PUT/PATCH /canonical-experiment-resource/{0} details".format(
                        kwargs.get('pk')))
            except PermissionDenied as exc:
                new_error(exc, request.user)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update an existing canonical-experiment-resource
        - experiment_id (fk)      - int
        - experiment_node_number  - int
        - node_type               - string
        - node_uhd                - string
        - node_vehicle            - string
        - resource_id (fk)        - int

        Permission:
        - user is_operator
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: remove an existing canonical-experiment-resource
        - experiment_id (fk)      - int
        - experiment_node_number  - int
        - node_type               - string
        - node_uhd                - string
        - node_vehicle            - string
        - resource_id (fk)        - int

        Permission:
        - user is_operator
        """
        raise MethodNotAllowed(method="DELETE: /canonical-experiment-resource/{int:pk}")

from datetime import datetime, timezone
from uuid import uuid4

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from portal.apps.experiments.models import AerpawExperiment
from portal.apps.projects.models import AerpawProject
from portal.apps.resources.api.serializers import ResourceSerializerDetail
from portal.apps.user_messages.user_messages import generate_user_messages_from_user_request
from portal.apps.user_requests.api.serializers import UserRequestSerializerDetail, UserRequestSerializerList
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.users.models import AerpawRolesEnum, AerpawUser


class UserRequestViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Resource
    - paginated list
    - retrieve one
    - create
    - update
    - delete
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AerpawUserRequest.objects.all().order_by('-created')
    serializer_class = ResourceSerializerDetail

    def get_queryset(self):
        experiment_id = self.request.query_params.get('experiment_id', None)
        project_id = self.request.query_params.get('project_id', None)
        request_type = self.request.query_params.get('request_type', None)
        role_user_id = self.request.query_params.get('role_user_id', None)
        show_completed = self.request.query_params.get('show_completed', None)
        user_id = self.request.query_params.get('user_id', None)
        q_filter = None
        if str(show_completed).casefold() == 'true':
            show_completed = True
        else:
            show_completed = False
        if experiment_id:
            q_filter = Q(request_type_id=experiment_id, request_type='experiment')
        if project_id:
            q_filter = Q(request_type_id=project_id, request_type='project')
        if request_type:
            q_filter = Q(request_type=request_type)
        if role_user_id:
            q_filter = Q(request_type_id=role_user_id, request_type='role')
        if user_id:
            q_filter = (Q(requested_by__id=user_id) | Q(received_by__id__in=[user_id]))

        if q_filter and show_completed:
            queryset = AerpawUserRequest.objects.filter(
                q_filter
            ).order_by('-created').distinct()
        elif q_filter and not show_completed:
            queryset = AerpawUserRequest.objects.filter(
                Q(is_approved__isnull=True) & q_filter
            ).order_by('-created').distinct()
        elif not q_filter and show_completed:
            queryset = AerpawUserRequest.objects.all().order_by('-created').distinct()
        else:
            queryset = AerpawUserRequest.objects.filter(
                Q(is_approved__isnull=True)
            ).order_by('-created').distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list user requests as paginated results
        - is_approved            - bool or NULL
        - received_by            - array of int
        - request_id             - int
        - request_note           - string
        - request_type           - string
        - request_type_id        - int
        - requested_by           - int
        - requested_date         - string

        @param experiment_id - user in experiment
        @param project_id = user in project
        @param request_type = user is_site_admin
        @param role_user_id = user is_site_admin
        @param show_completed = optional - default False
        @param user_id = user_id is user.id

        Permission:
        - user is_active
        """
        if request.user.is_active:
            # validate user request
            experiment_id = request.query_params.get('experiment_id', None)
            project_id = request.query_params.get('project_id', None)
            request_type = request.query_params.get('request_type', None)
            role_user_id = request.query_params.get('role_user_id', None)
            user_id = request.query_params.get('user_id', None)
            if experiment_id:
                # experiment must exist
                experiment = get_object_or_404(AerpawExperiment, pk=experiment_id)
                # user must be experiment creator or member
                if not experiment.is_creator(request.user) and not experiment.is_member(request.user):
                    raise PermissionDenied(
                        detail="PermissionDenied: unable to GET /requests list?experiment_id=...")
            if project_id:
                # project must exist
                project = get_object_or_404(AerpawProject, pk=project_id)
                # user must be project creator, owner or member
                if not project.is_creator(request.user) and not project.is_owner(
                        request.user) and not project.is_member(request.user):
                    raise PermissionDenied(
                        detail="PermissionDenied: unable to GET /requests list?project_id=...")
            if request_type:
                # user must be site_admin
                if not request.user.is_site_admin():
                    raise PermissionDenied(
                        detail="PermissionDenied: unable to GET /requests list?request_type=...")
                # request_type must be experiment, project or role
                if request_type not in [c[0] for c in AerpawUserRequest.RequestType.choices]:
                    raise ValidationError(
                        detail="ValidationError: request_type must be one of [{0}]".format(
                            [c[0] for c in AerpawUserRequest.RequestType.choices]))
            if role_user_id:
                # user_id must exist as valid user
                user = get_object_or_404(AerpawUser, pk=role_user_id)
                # user must be site admin
                if not request.user.is_site_admin():
                    raise PermissionDenied(
                        detail="PermissionDenied: unable to GET /requests list?role_user_id=...")
            if user_id:
                # user_id must exist as valid user
                user = get_object_or_404(AerpawUser, pk=user_id)
                # user must be site admin or be the user themselves
                if not request.user.is_site_admin() and user.id != request.user.id:
                    raise PermissionDenied(
                        detail="PermissionDenied: unable to GET /requests list?user_id=...")
            # fetch response
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = UserRequestSerializerList(page, many=True)
            else:
                serializer = UserRequestSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'is_approved': du.get('is_approved'),
                        'received_by': du.get('received_by'),
                        'request_id': du.get('request_id'),
                        'request_note': du.get('request_note'),
                        'request_type': du.get('request_type'),
                        'request_type_id': du.get('request_type_id'),
                        'requested_by': du.get('requested_by'),
                        'requested_date': str(du.get('requested_date'))
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /requests list")

    def create(self, request):
        """
        POST: create user request
        - completed_by (fk)      - int
        - completed_date         - string
        - * created              - string
        - * created_by           - string
        - * id                   - int
        - is_approved            - bool
        - modified               - string
        - modified_by            - string
        - * received_by (fk)     - int
        - * request_date         - string (same as created)
        - * request_note         - string
        - * request_type         - string in [experiment, project, role]
        - * request_type_id (fk) - int
        - * requested_by (fk)    - user_id
        - response_date          - UTC
        - response_note          - string
        - * uuid                 - string

        Reqeust data format:
        {
            "request_note": string,
            "request_type": string in ["experiment", "project", "role"],
            "request_type_id": int
        }

        Permission:
        - user is_active
        """
        user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        if request.user.is_active:
            # validate based on request_type
            request_type = request.data.get('request_type', None)
            if not request_type or request_type not in [c[0] for c in AerpawUserRequest.RequestType.choices]:
                raise ValidationError(
                    detail="ValidationError: request_type: must be one of {0}".format(
                        [c[0] for c in AerpawUserRequest.RequestType.choices]))
            request_type_id = request.data.get('request_type_id', None)
            if not request_type_id:
                raise ValidationError(
                    detail="ValidationError: must provide valid request_type_id")
            received_by = None
            # validate experiment request
            if request_type == AerpawUserRequest.RequestType.EXPERIMENT:
                experiment = get_object_or_404(AerpawExperiment.objects.all(), pk=request_type_id)
                project = experiment.project
                if not (project.is_creator(user) or project.is_member(user) or project.is_owner(user)):
                    raise ValidationError(
                        detail="ValidationError: user does not have required project membership")
                received_by = AerpawUser.objects.filter(
                    Q(id__in=experiment.experiment_membership.all()) |
                    Q(id=experiment.experiment_creator.id)
                ).distinct()
            # validate project request
            elif request_type == AerpawUserRequest.RequestType.PROJECT:
                project = get_object_or_404(AerpawProject.objects.all(), pk=request_type_id)
                if not project.is_public:
                    raise ValidationError(
                        detail="ValidationError: project is not accepting join requests")
                received_by = AerpawUser.objects.filter(
                    Q(id__in=project.project_owners()) |
                    Q(id=project.project_creator.id)
                ).distinct()
            # validate role request
            elif request_type == AerpawUserRequest.RequestType.ROLE:
                user = get_object_or_404(AerpawUser.objects.all(), pk=request_type_id)
                if user.id != request.user.id:
                    raise ValidationError(
                        detail="ValidationError: role requests can only be made by the user themselves")
                received_by = AerpawUser.objects.filter(
                    groups__name=AerpawRolesEnum.SITE_ADMIN.value
                ).all()

            if not received_by:
                raise ValidationError(
                    detail="ValidationError: must provide valid request_type_id")
            else:
                # create user_request
                user_request = AerpawUserRequest()
                user_request.created_by = user.username
                user_request.modified_by = user.username
                user_request.request_note = request.data.get('request_note', None)
                user_request.request_type = request_type
                user_request.request_type_id = request_type_id
                user_request.requested_by = request.user
                user_request.uuid = uuid4()
                user_request.save()
                for r in received_by:
                    user_request.received_by.add(r)
                user_request.save()
                generate_user_messages_from_user_request(request=request,
                                                         user_request=self.retrieve(request, pk=user_request.id).data)
                return self.retrieve(request, pk=user_request.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to POST /requests")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: user request as detailed result
        - completed_by           - int
        - completed_date         - string
        - is_approved            - bool or NULL
        - last_modified_by       - int
        - modified_date          - string
        - received_by            - array of int
        - request_id             - int
        - request_note           - string
        - request_type           - string
        - request_type_id        - int
        - requested_by           - int
        - requested_date         - string
        - response_date          - string
        - response_note          - string

        Permission:
        - user is_active
        """
        user_request = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_active and \
                (request.user in user_request.received_by.all() or request.user == user_request.requested_by):
            serializer = UserRequestSerializerDetail(user_request)
            du = dict(serializer.data)
            response_data = {
                'completed_by': du.get('completed_by'),
                'completed_date': str(du.get('completed_date')) if du.get('completed_date') else None,
                'is_approved': du.get('is_approved'),
                'last_modified_by': AerpawUser.objects.get(username=du.get('last_modified_by')).id,
                'modified_date': str(du.get('modified_date')) if du.get('modified_date') else None,
                'received_by': du.get('received_by'),
                'request_id': du.get('request_id'),
                'request_note': du.get('request_note'),
                'request_type': du.get('request_type'),
                'request_type_id': du.get('request_type_id'),
                'requested_by': du.get('requested_by'),
                'requested_date': str(du.get('requested_date')) if du.get('requested_date') else None,
                'response_date': str(du.get('response_date')) if du.get('response_date') else None,
                'response_note': du.get('response_note'),
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /requests/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: update existing resource
        - completed_by (fk)      - int
        - completed_date         - string
        - is_approved            - bool
        - modified               - string
        - modified_by            - string
        - response_date          - string
        - response_note          - string

        Reqeust data format:
        {
            "is_approved": boolean,
            "response_note": string
        }

        Permission:
        - user in received_by
        """
        user_request = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user in user_request.received_by.all():
            completed = False
            # check for is_approved
            if str(request.data.get('is_approved')).casefold() in ['true', 'false']:
                is_approved = True if str(request.data.get('is_approved')).casefold() == 'true' else False
                user_request.is_approved = is_approved
                completed = True
            if completed:
                user_request.completed_by = request.user
                user_request.completed_date = datetime.now(timezone.utc)
                user_request.modified_by = request.user.username
                user_request.response_date = datetime.now(timezone.utc)
                user_request.response_note = request.data.get('response_note')
                user_request.save()
                generate_user_messages_from_user_request(request=request,
                                                         user_request=self.retrieve(request, pk=user_request.id).data)
            return self.retrieve(request, pk=user_request.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to PUT/PATCH /requests/{0} details".format(kwargs.get('pk')))

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update existing resource
        - completed_by (fk)      - int
        - completed_date         - string
        - is_approved            - bool
        - modified               - string
        - modified_by            - string
        - response_date          - string
        - response_note          - string

        Reqeust data format:
        {
            "is_approved": boolean,
            "response_note": string
        }

        Permission:
        - user in received_by
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: soft delete existing project
        - is_approved            - False
        - response_note          - string

        Permission:
        - user in received_by or user is requested_by
        """
        user_request = get_object_or_404(self.queryset, pk=pk)
        if user_request.completed_date:
            raise ValidationError(
                detail="ValidationError: unable to DELETE /requests/{0} - request is already completed".format(pk))
        if request.user in user_request.received_by.all() or request.user == user_request.requested_by:
            user_request.completed_by = request.user
            user_request.completed_date = datetime.now(timezone.utc)
            user_request.is_approved = False
            user_request.modified_by = request.user.username
            user_request.response_date = datetime.now(timezone.utc)
            user_request.response_note = "RequestDeleted: by user {0}".format(request.user.username)
            user_request.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to DELETE /requests/{0}".format(pk))

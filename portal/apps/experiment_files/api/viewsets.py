from datetime import datetime, timezone

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from portal.apps.experiment_files.api.serializers import ExperimentFileSerializerDetail, ExperimentFileSerializerList
from portal.apps.experiment_files.models import ExperimentFile
from portal.apps.experiments.models import AerpawExperiment
from portal.apps.users.models import AerpawUser


class ExperimentFileViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    Experiment linked files
    - paginated list
    - retrieve one
    - create
    - update
    - delete
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = ExperimentFile.objects.all().order_by('file_name').distinct()
    serializer_class = ExperimentFileSerializerDetail

    def get_queryset(self):
        experiment_id = self.request.query_params.get('experiment_id', None)
        show_deleted = True if str(self.request.query_params.get('show_deleted', None)).casefold() == 'true' else False
        print(show_deleted)
        if experiment_id:
            experiment = get_object_or_404(AerpawExperiment, pk=experiment_id)
            if not experiment:
                raise NotFound(
                    detail="NotFound: unable to GET /experiment-files list")
            if show_deleted:
                queryset = ExperimentFile.objects.filter(
                    id__in=experiment.experiment_files.all()
                ).order_by('file_name').distinct()
            else:
                queryset = ExperimentFile.objects.filter(
                    is_deleted=False,
                    id__in=experiment.experiment_files.all()
                ).order_by('file_name').distinct()
        else:
            if show_deleted:
                queryset = ExperimentFile.objects.all().order_by('file_name').distinct()
            else:
                queryset = ExperimentFile.objects.filter(
                    is_deleted=False
                ).order_by('file_name').distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list experiment files as paginated results
        - file_id                - int
        - file_location          - string
        - file_name              - string
        - file_notes             - string
        - file_type              - string in ["ip_list", "ovpn"]
        - is_deleted             - bool

        Permission:
        - user is_experiment_member OR
        - user is_experiment_creator OR
        - user is_operator
        """
        if request.user.is_active:
            if request.user.is_operator():
                page = self.paginate_queryset(self.get_queryset())
            else:
                experiment = get_object_or_404(AerpawExperiment, pk=request.query_params.get('experiment_id', None))
                if not experiment.is_creator(request.user) and not experiment.is_member(request.user):
                    raise PermissionDenied(
                        detail="PermissionDenied: unable to GET /experiment-files list?experiment_id=...")
                page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = ExperimentFileSerializerList(page, many=True)
            else:
                serializer = ExperimentFileSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'file_id': du.get('file_id'),
                        'file_location': du.get('file_location'),
                        'file_name': du.get('file_name'),
                        'file_notes': du.get('file_notes'),
                        'file_type': du.get('file_type'),
                        'is_deleted': du.get('is_deleted')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /experiment-files list")

    def create(self, request):
        """
        POST: create new experiment file (* = required fields)
        - created_by             - string
        - created_date           - string
        - file_id                - int
        - file_location *        - string
        - file_name *            - string
        - file_notes             - string
        - file_type *            - string in ["ip_list", "ovpn"]
        - last_modified_by       - string
        - modified_date          - string

        Permission:
        - user is_operator
        """
        try:
            user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        except Exception as exc:
            raise ValidationError(
                detail="ValidationError: {0}".format(exc))
        if user.is_operator():
            # validate file_location
            file_location = request.data.get('file_location', None)
            if not file_location:
                raise ValidationError(
                    detail="file_location:  must include a Linked File Location")
            # validate file_name
            file_name = request.data.get('file_name', None)
            if not file_name:
                raise ValidationError(
                    detail="file_name:  must include a Linked File Name")
            # validate file_type
            file_type = request.data.get('file_type', None)
            if not file_type or file_type not in [c[0] for c in ExperimentFile.LinkedFileType.choices]:
                raise ValidationError(
                    detail="file_type:  must include a valid Linked File Type {0}".format(
                        [c[0] for c in ExperimentFile.LinkedFileType.choices]))
            # create experiment linked file
            linked_file = ExperimentFile()
            linked_file.created = datetime.now(timezone.utc)
            linked_file.created_by = user.username
            linked_file.file_location = file_location
            linked_file.file_name = file_name
            linked_file.file_type = file_type
            linked_file.modified_by = user.username
            linked_file.notes = request.data.get('file_notes', None)
            linked_file.save()

            return self.retrieve(request, pk=linked_file.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to POST /experiment-files")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve linked file as single result
        - created_by             - string
        - created_date           - string
        - file_id                - int
        - file_location *        - string
        - file_name *            - string
        - file_notes             - string
        - file_type *            - string in ["ip_list", "ovpn"]
        - is_deleted             - bool
        - last_modified_by       - string
        - modified_date          - string

        Permission:
        - user is_experiment_member OR
        - user is_experiment_creator OR
        - user is_operator
        """
        experiment_id = request.query_params.get('experiment_id', None)
        if request.user.is_operator() or experiment_id:
            if request.user.is_operator():
                linked_file = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
            elif experiment_id:
                experiment = get_object_or_404(self.queryset, pk=experiment_id)
                if not experiment.is_creator(request.user) and not experiment.is_member(request.user):
                    raise PermissionDenied(
                        detail="PermissionDenied: unable to GET /experiment-files/{0} list?experiment_id=...".format(
                            experiment_id))
                linked_file = get_object_or_404(self.get_queryset, pk=kwargs.get('pk'))

            serializer = ExperimentFileSerializerDetail(linked_file)
            du = dict(serializer.data)
            response_data = {
                'created_by': AerpawUser.objects.get(username=du.get('created_by')).id,
                'created_date': du.get('created_date'),
                'file_id': du.get('file_id'),
                'file_location': du.get('file_location'),
                'file_name': du.get('file_name'),
                'file_notes': du.get('file_notes'),
                'file_type': du.get('file_type'),
                'is_deleted': du.get('is_deleted'),
                'last_modified_by': AerpawUser.objects.get(username=du.get('last_modified_by')).id,
                'modified_date': str(du.get('modified_date'))
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /experiment-files/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: update an existing linked experiment file
        - file_location          - string
        - file_name              - string
        - file_notes             - string
        - file_type              - string in ["ip_list", "ovpn"]

        Permission:
        - user is_operator
        """
        linked_file = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.is_operator():
            modified = False
            # check for file_location
            if request.data.get('file_location', None):
                linked_file.file_location = request.data.get('file_location')
                modified = True
            # check for file_name
            if request.data.get('file_name', None):
                linked_file.file_name = request.data.get('file_name')
                modified = True
            # check for file_notes
            if request.data.get('file_notes', None):
                linked_file.notes = request.data.get('file_notes')
                modified = True
            # check for file_type
            if request.data.get('file_type', None):
                if request.data.get('file_type') not in [c[0] for c in ExperimentFile.LinkedFileType.choices]:
                    raise ValidationError(
                        detail="file_type:  must include a valid Linked File Type {0}".format(
                            [c[0] for c in ExperimentFile.LinkedFileType.choices]))
                linked_file.file_type = request.data.get('file_type')
                modified = True
            # save if modified
            if modified:
                linked_file.modified_by = request.user.email
                linked_file.save()
            return self.retrieve(request, pk=linked_file.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to PUT/PATCH /experiment-files/{0} details".format(kwargs.get('pk')))

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update an existing linked experiment file
        - file_location          - string
        - file_name              - string
        - file_notes             - string
        - file_type              - string in ["ip_list", "ovpn"]

        Permission:
        - user is_operator
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: soft delete existing linked file
        - is_deleted             - bool

        Permission:
        - user is_operator
        """
        linked_file = get_object_or_404(self.queryset, pk=pk)
        if request.user.is_operator():
            linked_file.is_deleted = True
            linked_file.modified_by = request.user.username
            linked_file.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to DELETE /experiment-files/{0}".format(pk))

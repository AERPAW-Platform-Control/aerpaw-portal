from urllib.parse import parse_qs, urlparse

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.request import Request

from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.projects.api.viewsets import ProjectViewSet
from portal.apps.projects.forms import ProjectCreateForm, ProjectMembershipForm
from portal.apps.projects.models import AerpawProject
from portal.apps.user_requests.api.viewsets import UserRequestViewSet
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.user_requests.user_requests import approve_project_join_request, deny_project_join_request
from portal.server.settings import DEBUG, REST_FRAMEWORK


@csrf_exempt
@login_required
def project_list(request):
    message = None
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        data_dict = {}
        if request.method == 'POST':
            if request.POST.get('request_join_project'):
                p = ProjectViewSet(request=request)
                proj = p.retrieve(request=request, pk=request.POST.get('request_join_project')).data
                ur_api_request = Request(request=HttpRequest())
                ur = UserRequestViewSet(request=ur_api_request)
                ur_api_request.user = request.user
                ur_api_request.method = 'POST'
                ur_api_request.data.update(
                    {'request_type': AerpawUserRequest.RequestType.PROJECT.value,
                     'request_type_id': request.POST.get('request_join_project'),
                     'request_note': '[{0}] - project join request'.format(proj.get('name'))})
                resp = ur.create(request=ur_api_request)
        elif request.method == 'GET':
            if request.GET.get('search'):
                data_dict['search'] = request.GET.get('search')
                search_term = request.GET.get('search')
            if request.GET.get('page'):
                data_dict['page'] = request.GET.get('page')
                current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        p = ProjectViewSet(request=request)
        projects = p.list(request=request)

        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if projects.data:
            projects = dict(projects.data)
            prev_url = projects.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    new_error(exc, request.user)
                    prev_page = 1
            next_url = projects.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    new_error(exc, request.user)
                    next_page = 1
            count = int(projects.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        else:
            projects = {}
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        error = new_error(exc, request.user)
        message = error.message
        projects = {}
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'project_list.html',
                  {
                      'user': request.user,
                      'projects': projects,
                      'item_range': item_range,
                      'message': message,
                      'next_page': next_page,
                      'prev_page': prev_page,
                      'search': search_term,
                      'count': count,
                      'debug': DEBUG
                  })


@csrf_exempt
@login_required
def project_detail(request, project_id):
    p = ProjectViewSet(request=request)
    message = None
    try:
        if request.method == "POST":
            if request.POST.get('approve_request_id'):
                if approve_project_join_request(request_id=int(request.POST.get('approve_request_id'))):
                    try:
                        # add user to project as project_member
                        p_obj = AerpawProject.objects.get(id=project_id)
                        ur_obj = AerpawUserRequest.objects.get(id=request.POST.get('approve_request_id'))
                        p_obj_members = [u.id for u in p_obj.project_members()]
                        p_obj_members.append(ur_obj.requested_by.id)
                        api_request = Request(request=HttpRequest())
                        api_request.data.update(
                            {'project_members': p_obj_members})
                        api_request.user = request.user
                        api_request.method = 'PUT'
                        p = ProjectViewSet(request=api_request)
                        p_resp = p.membership(request=api_request, pk=project_id)
                        # update user request to join project as approved
                        ur_api_request = Request(request=HttpRequest())
                        ur = UserRequestViewSet(request=ur_api_request)
                        ur_api_request.user = request.user
                        ur_api_request.method = 'PUT'
                        ur_api_request.data.update(
                            {'is_approved': True,
                             'response_note': request.POST.get('response_note', None)})
                        ur_resp = ur.update(request=ur_api_request, pk=request.POST.get('approve_request_id'))
                        return redirect('project_detail', project_id=project_id)
                    except Exception as exc:
                        error = new_error(exc, request.user)
                        message = error.message
            elif request.POST.get('deny_request_id'):
                if deny_project_join_request(request_id=int(request.POST.get('deny_request_id'))):
                    # update user request to join project as denied
                    ur_api_request = Request(request=HttpRequest())
                    ur = UserRequestViewSet(request=ur_api_request)
                    ur_api_request.user = request.user
                    ur_api_request.method = 'PUT'
                    ur_api_request.data.update(
                        {'is_approved': False,
                         'response_note': request.POST.get('response_note', None)})
                    resp = ur.update(request=ur_api_request, pk=request.POST.get('deny_request_id'))
            elif request.POST.get('delete-project') == "true":
                project = p.destroy(request=request, pk=project_id).data
                return redirect('project_list')
        project = p.retrieve(request=request, pk=project_id).data
        # get experiments
        if project.get('membership').get('is_project_creator') or project.get('membership').get('is_project_owner') or \
                project.get('membership').get('is_project_member') or request.user.is_operator():
            experiments = p.experiments(request=request, pk=project_id).data
        else:
            experiments = None
        # get join requests
        if project.get('membership').get('is_project_creator') or project.get('membership').get('is_project_owner'):
            ur_api_request = Request(request=HttpRequest())
            ur_api_request.user = request.user
            ur_api_request.query_params.update({'project_id': project_id})
            ur_api_request.method = 'GET'
            ur = UserRequestViewSet(request=ur_api_request)
            user_requests = ur.list(request=ur_api_request)
            if user_requests.data:
                user_requests = dict(user_requests.data)
            else:
                user_requests = {}
        else:
            user_requests = {}
    except Exception as exc:
        error = new_error(exc, request.user)
        message = error.message
        project = None
        experiments = None
        user_requests = None
    return render(request,
                  'project_detail.html',
                  {
                      'user': request.user,
                      'project': project,
                      'experiments': experiments,
                      'user_requests': user_requests,
                      'message': message,
                      'debug': DEBUG
                  })


@csrf_exempt
@login_required
def project_create(request):
    message = None
    if request.method == "POST":
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_public', '') == 'on':
                    data_dict.update({'is_public': 'true'})
                else:
                    data_dict.update({'is_public': 'false'})
                request.data.update(data_dict)
                p = ProjectViewSet(request=request)
                request.data.update(data_dict)
                project = p.create(request=request).data
                return redirect('project_detail', project_id=project.get('project_id', 9999))
            except Exception as exc:
                error = new_error(exc, request.user)
                message = error.message
    else:
        form = ProjectCreateForm()
    return render(request,
                  'project_create.html',
                  {
                      'form': form,
                      'message': message
                  })


@csrf_exempt
@login_required
def project_edit(request, project_id):
    message = None
    if request.method == "POST":
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_public', '') == 'on':
                    data_dict.update({'is_public': 'true'})
                else:
                    data_dict.update({'is_public': 'false'})
                request.data.update(data_dict)
                p = ProjectViewSet(request=request)
                request.data.update(data_dict)
                project = p.partial_update(request=request, pk=project_id)
                return redirect('project_detail', project_id=project_id)
            except Exception as exc:
                error = new_error(exc, request.user)
                message = error.message
    else:
        project = get_object_or_404(AerpawProject, id=project_id)
        is_project_creator = project.is_creator(request.user)
        is_project_owner = project.is_owner(request.user)
        form = ProjectCreateForm(instance=project)
    return render(request,
                  'project_edit.html',
                  {
                      'form': form,
                      'message': message,
                      'project_id': project_id,
                      'is_project_creator': is_project_creator,
                      'is_project_owner': is_project_owner
                  })


@csrf_exempt
@login_required
def project_members(request, project_id):
    message = None
    project = get_object_or_404(AerpawProject, id=project_id)
    is_project_creator = project.is_creator(request.user)
    is_project_owner = project.is_owner(request.user)
    if request.method == "POST":
        form = ProjectMembershipForm(request.POST, instance=project)
        if form.is_valid():
            try:
                api_request = Request(request=HttpRequest())
                api_request.data.update({'project_members': [int(i) for i in request.POST.getlist('project_members')]})
                api_request.user = request.user
                api_request.method = 'PUT'
                p = ProjectViewSet(request=api_request)
                project = p.membership(request=api_request, pk=project_id)
                return redirect('project_detail', project_id=project_id)
            except Exception as exc:
                error = new_error(exc, request.user)
                message = error.message
    else:
        initial_dict = {
            'project_members': list(project.project_members())
        }
        form = ProjectMembershipForm(instance=project, initial=initial_dict)
    return render(request,
                  'project_members.html',
                  {
                      'form': form,
                      'message': message,
                      'project_id': project_id,
                      'is_project_creator': is_project_creator,
                      'is_project_owner': is_project_owner
                  })


@csrf_exempt
@login_required
def project_owners(request, project_id):
    message = None
    project = get_object_or_404(AerpawProject, id=project_id)
    is_project_creator = project.is_creator(request.user)
    is_project_owner = project.is_owner(request.user)
    if request.method == "POST":
        form = ProjectMembershipForm(request.POST, instance=project)
        if form.is_valid():
            try:
                api_request = Request(request=HttpRequest())
                api_request.data.update({'project_owners': [int(i) for i in request.POST.getlist('project_owners')]})
                api_request.user = request.user
                api_request.method = 'PUT'
                p = ProjectViewSet(request=api_request)
                project = p.membership(request=api_request, pk=project_id)
                return redirect('project_detail', project_id=project_id)
            except Exception as exc:
                error = new_error(exc, request.user)
                message = error.message
    else:
        initial_dict = {
            'project_owners': list(project.project_owners())
        }
        form = ProjectMembershipForm(instance=project, initial=initial_dict)
    return render(request,
                  'project_owners.html',
                  {
                      'form': form,
                      'message': message,
                      'project_id': project_id,
                      'is_project_creator': is_project_creator,
                      'is_project_owner': is_project_owner
                  })

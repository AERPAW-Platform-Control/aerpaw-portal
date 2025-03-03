import calendar, traceback, sys, re

from urllib.parse import parse_qs, urlparse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, QueryDict, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from rest_framework.request import Request
from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.experiment_info.form_dashboard import new_experiment_form_dashboard, field_trip_form

from portal.apps.experiments.api.experiment_utils import to_retired

from portal.apps.experiments.api.viewsets import CanonicalExperimentResourceViewSet, OnDemandSessionViewSet, \
    ExperimentViewSet, ScheduledSessionViewSet
from portal.apps.experiments.calendar import SandboxCalendar
from portal.apps.experiments.dashboard import evaluate_dashboard_action, evaluate_session_dashboard_action, get_dashboard_buttons, get_session_dashboard_buttons
from portal.apps.experiments.forms import ExperimentCreateForm, ExperimentEditForm, ExperimentFilesForm, \
    ExperimentMembershipForm, ExperimentResourceTargetModifyForm, ExperimentResourceTargetsForm
from portal.apps.experiments.models import AerpawExperiment, CanonicalExperimentResource, OnDemandSession, ScheduledSession
from portal.apps.projects.api.viewsets import ProjectViewSet
from portal.apps.resources.models import AerpawResource
from portal.apps.user_requests.api.viewsets import UserRequestViewSet
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.user_requests.user_requests import approve_experiment_join_request, deny_experiment_join_request
from portal.server.download_utils import download_sftp_experiment_file
from portal.server.settings import DEBUG, REST_FRAMEWORK


@csrf_exempt
@login_required
def experiment_list(request):
    message = None
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        data_dict = {}
        if request.method == 'POST':
            if request.POST.get('request_join_experiment'):
                e = ExperimentViewSet(request=request)
                exp = e.retrieve(request=request, pk=request.POST.get('request_join_experiment')).data
                ur_api_request = Request(request=HttpRequest())
                ur = UserRequestViewSet(request=ur_api_request)
                ur_api_request.user = request.user
                ur_api_request.method = 'POST'
                ur_api_request.data.update(
                    {'request_type': AerpawUserRequest.RequestType.EXPERIMENT.value,
                     'request_type_id': request.POST.get('request_join_experiment'),
                     'request_note': '[{0}] - experiment join request'.format(exp.get('name'))})
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
        e = ExperimentViewSet(request=request)
        experiments = e.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if experiments.data:
            experiments = dict(experiments.data)
            prev_url = experiments.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    new_error(exc, request.user)
                    prev_page = 1
            next_url = experiments.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    new_error(exc, request.user)
                    next_page = 1
            count = int(experiments.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        else:
            experiments = {}
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        new_error(exc, request.user)
        experiments = {}
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'experiment_list.html',
                  {
                      'user': request.user,
                      'experiments': experiments,
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
def experiment_detail(request, experiment_id):
    e = ExperimentViewSet(request=request)
    message = None
    try:
        experiment = e.retrieve(request=request, pk=experiment_id).data
        if request.method == "POST":
            try:
                evaluate_dashboard_action(request)
            except Exception as exc:
                new_error(exc, request.user)
            if request.POST.get('approve_request_id'):
                if approve_experiment_join_request(request_id=int(request.POST.get('approve_request_id'))):
                    try:
                        # add user to experiment as experiment_member
                        e_obj = AerpawExperiment.objects.get(id=experiment_id)
                        ur_obj = AerpawUserRequest.objects.get(id=request.POST.get('approve_request_id'))
                        e_obj_members = [u.id for u in e_obj.experiment_members()]
                        e_obj_members.append(ur_obj.requested_by.id)
                        api_request = Request(request=HttpRequest())
                        api_request.data.update(
                            {'experiment_members': e_obj_members})
                        api_request.user = request.user
                        api_request.method = 'PUT'
                        e = ExperimentViewSet(request=api_request)
                        e_resp = e.membership(request=api_request, pk=experiment_id)
                        # update user request to join experiment as approved
                        ur_api_request = Request(request=HttpRequest())
                        ur = UserRequestViewSet(request=ur_api_request)
                        ur_api_request.user = request.user
                        ur_api_request.method = 'PUT'
                        ur_api_request.data.update(
                            {'is_approved': True,
                             'response_note': request.POST.get('response_note', None)})
                        ur_resp = ur.update(request=ur_api_request, pk=request.POST.get('approve_request_id'))
                        return redirect('experiment_detail', experiment_id=experiment_id)
                    except Exception as exc:
                        new_error(exc, request.user)
            elif request.POST.get('deny_request_id'):
                if deny_experiment_join_request(request_id=int(request.POST.get('deny_request_id'))):
                    # TODO: placeholder for member check or other login
                    ur_api_request = Request(request=HttpRequest())
                    ur = UserRequestViewSet(request=ur_api_request)
                    ur_api_request.user = request.user
                    ur_api_request.method = 'PUT'
                    ur_api_request.data.update(
                        {'is_approved': False,
                         'response_note': request.POST.get('response_note', None)})
                    resp = ur.update(request=ur_api_request, pk=request.POST.get('deny_request_id'))
            elif request.POST.get('file_id'):
                try:
                    response = download_sftp_experiment_file(
                        int(request.user.id), int(experiment_id), int(request.POST.get('file_id'))
                    )
                    return response
                except Exception as exc:
                    new_error(exc, request.user)
            elif request.POST.get('retire_experiment') == "true":
                request.data = QueryDict('', mutable=True)
                request.data.update({'is_retired': 'true'})
                e = ExperimentViewSet(request=request)
                exp = e.partial_update(request=request, pk=experiment_id)
                to_retired(request, experiment=AerpawExperiment.objects.get(id=experiment_id))
                return redirect('experiment_list')
        # get canonical experiment resource definitions
        try:
            resources = []
            request.query_params = QueryDict('', mutable=True)
            request.query_params.update({'experiment_id': experiment_id})
            for res_id in experiment.get('resources'):
                request.query_params.update({'resource_id': res_id})
                r = CanonicalExperimentResourceViewSet(request=request)
                res = r.list(request=request)
                if res.data:
                    resources.append(res.data.get('results')[0])
            resources.sort(key=lambda x: x.get('experiment_node_number'))
        except Exception as exc:
            resources = []
            new_error(exc, request.user)
        # get join requests
        if experiment.get('membership').get('is_experiment_creator') or \
                experiment.get('membership').get('is_experiment_member'):
            ur_api_request = Request(request=HttpRequest())
            ur_api_request.user = request.user
            ur_api_request.query_params.update({'experiment_id': experiment_id})
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
        new_error(exc, request.user)
        experiment = None
        resources = []
        user_requests = {}
    dashboard_buttons = get_dashboard_buttons(request, experiment_id=experiment_id)
    try:
        session_obj = OnDemandSession.objects.filter(
            experiment_id=experiment_id
        ).order_by('-created').first()
        if session_obj is not None:
            if session_obj.is_active:
                s = OnDemandSessionViewSet(request=request)
                session = s.retrieve(request=request, pk=session_obj.pk).data
            else:
                session = {}
                if not session_obj.start_date_time:
                    message = 'DeploymentError: most recent deployment attempt was cancelled by user/operator'
        else:
            # If there is no current experiment session
            session = {}
    except Exception as exc:
        session = {}
        new_error(exc, request.user)
    sandbox_calendar = SandboxCalendar().get_calendar()
    return render(request,
                  'experiment_detail.html',
                  {
                      'user': request.user,
                      'experiment': experiment,
                      'resources': resources,
                      'buttons': dashboard_buttons,
                      'session': session,
                      'user_requests': user_requests,
                      'message': message,
                      'debug': DEBUG,
                      'sandbox_calendar': sandbox_calendar,
                  })


@csrf_exempt
@login_required
def experiment_create(request):
    message = None
    project = None
    if request.method == "POST":
        try:
            project_id = request.GET.get('project_id')
            p = ProjectViewSet()
            project = p.retrieve(request=request, pk=project_id).data
            form = new_experiment_form_dashboard(request, project_id)
            if 'redirect' in form.keys():
                return redirect(form['redirect'], experiment_id=form['experiment_id'])
            if 'template' in form.keys():
                form = form['template']
        except Exception as exc:
            new_error(exc, request.user)
    else:
        project_id = request.GET.get('project_id')
        p = ProjectViewSet()
        project = p.retrieve(request=request, pk=project_id).data
        #form = ExperimentCreateForm(initial={'project_id': project_id})

        form = new_experiment_form_dashboard(request, project_id)
        form = form['template']
    return render(request,
                  'experiment_create.html',
                  {
                      'form': form,
                      'message': message,
                      'project': project
                  })


@csrf_exempt
@login_required
def experiment_edit(request, experiment_id):
    message = 'INFO: selecting IS_RETIRED will permanently disable the experiment'
    experiment = get_object_or_404(AerpawExperiment, id=experiment_id)
    p = ProjectViewSet()
    project = p.retrieve(request=request, pk=experiment.project.id).data
    if request.method == "POST":
        form = ExperimentEditForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_retired', '') == 'on':
                    data_dict.update({'is_retired': 'true'})
                else:
                    data_dict.update({'is_retired': 'false'})
                request.data.update(data_dict)
                e = ExperimentViewSet(request=request)
                request.data.update(data_dict)
                experiment = e.partial_update(request=request, pk=experiment_id)
                return redirect('experiment_detail', experiment_id=experiment_id)
            except Exception as exc:
                new_error(exc, request.user)
    else:
        form = ExperimentEditForm(instance=experiment, initial={'project_id': project.get('project_id')})
    return render(request,
                  'experiment_edit.html',
                  {
                      'form': form,
                      'message': message,
                      'experiment_id': experiment_id,
                      'project': project
                  })


@csrf_exempt
@login_required
def experiment_members(request, experiment_id):
    message = None
    experiment = get_object_or_404(AerpawExperiment, id=experiment_id)
    is_experiment_creator = experiment.is_creator(request.user)
    is_experiment_member = experiment.is_member(request.user)
    if request.method == "POST":
        form = ExperimentMembershipForm(request.POST, instance=experiment)
        if form.is_valid():
            try:
                api_request = Request(request=HttpRequest())
                api_request.data.update(
                    {'experiment_members': [int(i) for i in request.POST.getlist('experiment_members')]})
                api_request.user = request.user
                api_request.method = 'PUT'
                e = ExperimentViewSet(request=api_request)
                experiment = e.membership(request=api_request, pk=experiment_id)
                return redirect('experiment_detail', experiment_id=experiment_id)
            except Exception as exc:
                new_error(exc, request.user)
    else:
        if experiment.experiment_state == 'saved':
            initial_dict = {
                'experiment_members': list(experiment.experiment_members())
            }
            form = ExperimentMembershipForm(instance=experiment, initial=initial_dict)
        else:
            form = None
            message = 'The experiment must not be in an active session in order to edit its members.  The experiment must be in the saved state.'
    return render(request,
                  'experiment_members.html',
                  {
                      'form': form,
                      'message': message,
                      'experiment_id': experiment_id,
                      'experiment_state': experiment.experiment_state,
                      'is_experiment_creator': is_experiment_creator,
                      'is_experiment_member': is_experiment_member
                  })


@csrf_exempt
@login_required
def experiment_resource_list(request, experiment_id):
    #message = 'INFO: Be sure to properly configure "Node UHD" and "Node Vehicle"'
    message = ''
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        data_dict = {'experiment_id': experiment_id}
        if request.GET.get('search'):
            data_dict['search'] = request.GET.get('search')
            search_term = request.GET.get('search')
        if request.GET.get('page'):
            data_dict['page'] = request.GET.get('page')
            current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        r = CanonicalExperimentResourceViewSet(request=request)
        resources = r.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if resources.data:
            resources = dict(resources.data)
            prev_url = resources.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    new_error(exc, request.user)
                    prev_page = 1
            next_url = resources.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    new_error(exc, request.user)
                    next_page = 1
            count = int(resources.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        else:
            resources = {}
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        new_error(exc, request.user)
        resources = {}
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'experiment_resource_list.html',
                  {
                      'user': request.user,
                      'resources': resources,
                      'experiment_id': experiment_id,
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
def experiment_resource_targets(request, experiment_id):
    message = None
    experiment = get_object_or_404(AerpawExperiment, id=experiment_id)
    is_experiment_creator = experiment.is_creator(request.user)
    is_experiment_member = experiment.is_member(request.user)
    if request.method == "POST":
        all_resources = AerpawResource.objects.all().order_by('name')
        cc_resources = [resource for resource in all_resources if resource.hostname[:-1] == 'node-cc']
        lw_resources = [resource for resource in all_resources if resource.hostname[:7] == 'node-lw']
        lpn_resources = [resource for resource in all_resources if resource.name[:3] == 'LPN']
        spn_resources = [resource for resource in all_resources if resource.name[:3] == 'SPN']
        acn_resources = [resource for resource in all_resources if resource.resource_type == 'ACN']
        experiment_resources = experiment.resources.all()
        canonical_resources = CanonicalExperimentResource.objects.filter(experiment__id=experiment.id).order_by('experiment_node_number')
        context={
            'all_resources': AerpawResource.objects.all().order_by('name'),
            'cc_resources': cc_resources,
            'lw_resources': lw_resources,
            'lpn_resources': lpn_resources,
            'spn_resources': spn_resources,
            'acn_resources': acn_resources,
            'experiment_resources': experiment_resources,
            'canonical_resources': canonical_resources,
        }
        form = render_to_string('experiments/forms/experiment_resource_targets_form.html', context)

        try:
            api_request = Request(request=HttpRequest())
            api_request.data.update({
                    'experiment_resources': [int(i) for i in request.POST.getlist('resource_id')],
                    'node_numbers':[i for i in request.POST.getlist('node_number')],
                 })
            print(f'node_numbers: {api_request.data.get("node_numbers")}')
            api_request.user = request.user
            api_request.method = 'PUT'
            e = ExperimentViewSet(request=api_request)
            exp = e.resources(request=api_request, pk=experiment_id)
            return redirect('experiment_resource_list', experiment_id=experiment_id)
        except Exception as exc:
            new_error(exc, request.user)


        #form = ExperimentResourceTargetsForm(request.POST, instance=experiment)
        #if form.is_valid():
        """     try:
                api_request = Request(request=HttpRequest())
                api_request.data.update(
                    {'experiment_resources': [int(i) for i in request.POST.getlist('experiment_resources')]})
                api_request.user = request.user
                api_request.method = 'PUT'
                e = ExperimentViewSet(request=api_request)
                exp = e.resources(request=api_request, pk=experiment_id)
                return redirect('experiment_resource_list', experiment_id=experiment_id)
            except Exception as exc:
                message = exc """
    else:
        initial_dict = {
            'experiment_resources': list(experiment.resources.all().values_list('id', flat=True))
        }
        # form = ExperimentResourceTargetsForm(instance=experiment, initial=initial_dict)
        all_resources = AerpawResource.objects.all().order_by('name')
        cc_resources = [resource for resource in all_resources if resource.name[:2] == 'CC']
        lw_resources = [resource for resource in all_resources if resource.name[:2] == 'LW']
        lpn_resources = [resource for resource in all_resources if resource.name[:3] == 'LPN']
        spn_resources = [resource for resource in all_resources if resource.name[:3] == 'SPN']
        acn_resources = [resource for resource in all_resources if resource.resource_type == 'ACN']
        print(f'Aerpaw Cloud Nodes= {acn_resources}')
        experiment_resources = experiment.resources.all()
        canonical_resources = CanonicalExperimentResource.objects.filter(experiment__id=experiment.id).order_by('experiment_node_number')
        context={
            'all_resources': AerpawResource.objects.all().order_by('name'),
            'cc_resources': cc_resources,
            'lw_resources': lw_resources,
            'lpn_resources': lpn_resources,
            'spn_resources': spn_resources,
            'acn_resources': acn_resources,
            'experiment_resources': experiment_resources,
            'canonical_resources': canonical_resources,
        }
        form = render_to_string('experiments/forms/experiment_resource_targets_form.html', context)
    return render(request,
                  'experiments/experiment_resource_targets.html',
                  {
                      'form': form,
                      'message': message,
                      'experiment_id': experiment_id,
                      'is_experiment_creator': is_experiment_creator,
                      'is_experiment_member': is_experiment_member
                  })


@csrf_exempt
@login_required
def experiment_resource_target_edit(request, experiment_id, canonical_experiment_resource_id):
    message = None
    cer = get_object_or_404(CanonicalExperimentResource, id=canonical_experiment_resource_id)
    is_experiment_creator = cer.experiment.is_creator(request.user)
    is_experiment_member = cer.experiment.is_member(request.user)
    if request.method == "POST":
        form = ExperimentResourceTargetModifyForm(request.POST, instance=cer)
        if form.is_valid():
            try:
                api_request = Request(request=HttpRequest())
                if request.POST.get('node_display_name'):
                    api_request.data.update({'node_display_name': request.POST.get('node_display_name')})
                if request.POST.get('node_uhd'):
                    api_request.data.update({'node_uhd': request.POST.get('node_uhd')})
                if request.POST.get('node_vehicle'):
                    api_request.data.update({'node_vehicle': request.POST.get('node_vehicle')})
                api_request.user = request.user
                api_request.method = 'PUT'
                c = CanonicalExperimentResourceViewSet(request=api_request)
                u_cer = c.update(request=api_request, pk=canonical_experiment_resource_id)
                return redirect('experiment_resource_list', experiment_id=experiment_id)
            except Exception as exc:
                error = new_error(exc, request.user)
    else:
        initial_dict = {
            'name': cer.resource.name,
            'node_display_name': cer.node_display_name,
            'node_type': cer.node_type,
            'node_uhd': cer.node_uhd,
            'node_vehicle': cer.node_vehicle
        }
        form = ExperimentResourceTargetModifyForm(instance=cer, initial=initial_dict)
    return render(request,
                  'experiment_resource_target_edit.html',
                  {
                      'form': form,
                      'message': message,
                      'canonical_experiment_resource_id': canonical_experiment_resource_id,
                      'experiment_id': experiment_id,
                      'is_experiment_creator': is_experiment_creator,
                      'is_experiment_member': is_experiment_member,
                      'cer': cer
                  })


@csrf_exempt
@login_required
def experiment_files(request, experiment_id):
    message = None
    experiment = get_object_or_404(AerpawExperiment, id=experiment_id)
    is_operator = request.user.is_operator()
    if request.method == "POST":
        form = ExperimentFilesForm(request.POST, instance=experiment)
        if form.is_valid():
            try:
                api_request = Request(request=HttpRequest())
                api_request.data.update(
                    {'experiment_files': [int(i) for i in request.POST.getlist('experiment_files')]})
                api_request.user = request.user
                api_request.method = 'PUT'
                e = ExperimentViewSet(request=api_request)
                experiment = e.files(request=api_request, pk=experiment_id)
                return redirect('experiment_detail', experiment_id=experiment_id)
            except Exception as exc:
                error = new_error(exc, request.user)
    else:
        initial_dict = {
            'experiment_files': [f.id for f in experiment.experiment_files.all()]
        }
        form = ExperimentFilesForm(instance=experiment, initial=initial_dict)
    return render(request,
                  'experiment_files.html',
                  {
                      'form': form,
                      'message': message,
                      'experiment_id': experiment_id,
                      'is_operator': is_operator
                  })


@csrf_exempt
@login_required
def experiment_sessions(request, experiment_id):
    message = None
    experiment = get_object_or_404(AerpawExperiment, id=experiment_id)
    user = request.user
    is_operator = False
    dashboard_buttons = None
    if user.groups.filter(name='operator').exists():
        try:
            is_operator = True
            evaluate_session_dashboard_action(request)    
        except Exception as exc:
            new_error(exc, request.user)
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        data_dict = {'experiment_id': experiment.id}
        if request.GET.get('search'):
            data_dict['search'] = request.GET.get('search')
            search_term = request.GET.get('search')
        if request.GET.get('page'):
            data_dict['page'] = request.GET.get('page')
            current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        
        scheduled_e = ScheduledSessionViewSet(request=request)
        scheduled_sessions = scheduled_e.get_queryset()
        scheduled_session_ids = scheduled_sessions.values_list('id', flat=True)

        e = OnDemandSessionViewSet(request=request)
        sessions = e.get_queryset().exclude(id__in=scheduled_session_ids)

        # Combines and retrieves data for ScheduledSessions and OnDemandSessions
        all_sessions = scheduled_e.sessions_list(request=request, many=True, ops_sessions=scheduled_sessions, sessions=sessions)
        



        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if all_sessions.data:
            all_sessions = dict(all_sessions.data)
            dashboard_buttons = get_session_dashboard_buttons(request, session_id=all_sessions['results'][0]['session_id'] )
            results = all_sessions['results']
            all_sessions['results'] = sorted(results, key=lambda x: x['session_id'], reverse=True)
            prev_url = all_sessions.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    print(f'1.) experiments/views experiment_sessions {exc}')
                    new_error(exc, request.user)
                    prev_page = 1
            next_url = all_sessions.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    print(f'2.) experiments/views experiment_sessions {exc}')
                    error = new_error(exc, request.user)
                    message = error.message
                    next_page = 1
            count = int(all_sessions.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        else:
            all_sessions = {}
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
        dashboard_buttons = get_session_dashboard_buttons(request, session_id=None)
        
    except Exception as exc:
        error = new_error(exc, request.user)
        all_sessions = None
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
        dashboard_buttons = None
    return render(request,
                  'experiment_sessions.html',
                  {
                      'user': user,
                      'is_operator':is_operator,
                      'experiment': experiment,
                      'end_testbed_session_form':field_trip_form(experiment_id),
                      'sessions': all_sessions,
                      'item_range': item_range,
                      'message': message,
                      'next_page': next_page,
                      'prev_page': prev_page,
                      'search': search_term,
                      'count': count,
                      'buttons': dashboard_buttons,
                      'debug': DEBUG
                  })


@csrf_exempt
@login_required
def session_detail(request, experiment_id, session_id):
    message = None
    
    try:
        sessions = ScheduledSession.objects.filter(id=session_id)
        if len(sessions) == 0:
            session = OnDemandSession.objects.get(id=session_id)
        else:
            session = sessions[0]
    except Exception as exc:
        new_error(exc, request.user)
        session = None
    

    return render(request,
                  'session_detail.html',
                  {
                      'user': request.user,
                      'session': session,
                      'message': message,
                      'debug': DEBUG
                  })


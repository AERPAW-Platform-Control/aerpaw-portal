from urllib.parse import parse_qs, urlparse

from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from portal.apps.experiment_files.api.viewsets import ExperimentFileViewSet
from portal.apps.experiment_files.forms import ExperimentFileCreateForm
from portal.apps.experiment_files.models import ExperimentFile
from portal.server.settings import DEBUG, REST_FRAMEWORK


@csrf_exempt
@login_required
def experiment_file_list(request):
    message = None
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        data_dict = {}
        if request.GET.get('search'):
            data_dict['search'] = request.GET.get('search')
            search_term = request.GET.get('search')
        if request.GET.get('page'):
            data_dict['page'] = request.GET.get('page')
            current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        f = ExperimentFileViewSet(request=request)
        experiment_files = f.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if experiment_files.data:
            experiment_files = dict(experiment_files.data)
            prev_url = experiment_files.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    prev_page = 1
            next_url = experiment_files.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    next_page = 1
            count = int(experiment_files.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        else:
            experiment_files = {}
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        message = exc
        experiment_files = {}
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'experiment_file_list.html',
                  {
                      'user': request.user,
                      'experiment_files': experiment_files,
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
def experiment_file_detail(request, file_id):
    message = None
    try:
        request.query_params = QueryDict('', mutable=True)
        f = ExperimentFileViewSet(request=request)
        if request.method == "POST":
            if request.POST.get('delete-file') == "true":
                experiment_file = f.destroy(request=request, pk=file_id).data
                return redirect('experiment_file_list')
        experiment_file = f.retrieve(request=request, pk=file_id).data
    except Exception as exc:
        message = exc
        experiment_file = None
    return render(request,
                  'experiment_file_detail.html',
                  {
                      'user': request.user,
                      'experiment_file': experiment_file,
                      'message': message,
                      'debug': DEBUG
                  })


@csrf_exempt
@login_required
def experiment_file_create(request):
    message = None
    if request.method == "POST":
        form = ExperimentFileCreateForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                request.query_params = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_active', '') == 'on':
                    data_dict.update({'is_active': 'true'})
                else:
                    data_dict.update({'is_active': 'false'})
                request.data.update(data_dict)
                r = ExperimentFileViewSet(request=request)
                experiment_file = r.create(request=request).data
                print(experiment_file)
                return redirect('experiment_file_detail', file_id=experiment_file.get('file_id', 9999))
            except Exception as exc:
                message = exc
    else:
        form = ExperimentFileCreateForm()
    return render(request,
                  'experiment_file_create.html',
                  {
                      'form': form,
                      'message': message
                  })


@csrf_exempt
@login_required
def experiment_file_edit(request, file_id):
    message = None
    if request.method == "POST":
        form = ExperimentFileCreateForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                request.query_params = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_active', '') == 'on':
                    data_dict.update({'is_active': 'true'})
                else:
                    data_dict.update({'is_active': 'false'})
                request.data.update(data_dict)
                r = ExperimentFileViewSet(request=request)
                request.data.update(data_dict)
                experiment_file = r.partial_update(request=request, pk=file_id)
                return redirect('experiment_file_detail', file_id=file_id)
            except Exception as exc:
                message = exc
    else:
        experiment_file = get_object_or_404(ExperimentFile, id=file_id)
        form = ExperimentFileCreateForm(instance=experiment_file)
    return render(request,
                  'experiment_file_edit.html',
                  {
                      'form': form,
                      'message': message,
                      'file_id': file_id
                  })

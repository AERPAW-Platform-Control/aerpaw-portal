from urllib.parse import parse_qs, urlparse

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, QueryDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.request import Request

from portal.apps.user_requests.api.viewsets import UserRequestViewSet
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.user_requests.user_requests import approve_user_role_request, deny_user_role_request
from portal.server.settings import DEBUG, REST_FRAMEWORK


@csrf_exempt
@login_required
def user_role_reqeust_list(request):
    message = None
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        if request.method == 'POST':
            if request.POST.get('approve_request_id'):
                if approve_user_role_request(request_id=int(request.POST.get('approve_request_id'))):
                    ur_api_request = Request(request=HttpRequest())
                    ur = UserRequestViewSet(request=ur_api_request)
                    ur_api_request.user = request.user
                    ur_api_request.method = 'PUT'
                    ur_api_request.data.update(
                        {'is_approved': True,
                         'response_note': request.POST.get('response_note', None)})
                    resp = ur.update(request=ur_api_request, pk=request.POST.get('approve_request_id'))
            if request.POST.get('deny_request_id'):
                if deny_user_role_request(request_id=int(request.POST.get('deny_request_id'))):
                    ur_api_request = Request(request=HttpRequest())
                    ur = UserRequestViewSet(request=ur_api_request)
                    ur_api_request.user = request.user
                    ur_api_request.method = 'PUT'
                    ur_api_request.data.update(
                        {'is_approved': False,
                         'response_note': request.POST.get('response_note', None)})
                    resp = ur.update(request=ur_api_request, pk=request.POST.get('deny_request_id'))
        data_dict = {'request_type': AerpawUserRequest.RequestType.ROLE.value}
        if request.GET.get('page'):
            data_dict['page'] = request.GET.get('page')
            current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        ur = UserRequestViewSet(request=request)
        user_requests = ur.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if user_requests.data:
            user_requests = dict(user_requests.data)
            prev_url = user_requests.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    prev_page = 1
            next_url = user_requests.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    next_page = 1
            count = int(user_requests.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        else:
            user_requests = {}
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        message = exc
        user_requests = {}
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'user_role_request_list.html',
                  {
                      'user': request.user,
                      'user_requests': user_requests,
                      'item_range': item_range,
                      'message': message,
                      'next_page': next_page,
                      'prev_page': prev_page,
                      'search': search_term,
                      'count': count,
                      'debug': DEBUG
                  })

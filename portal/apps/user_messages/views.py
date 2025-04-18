from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.request import Request

from portal.apps.error_handling.api.error_utils import catch_exception
from portal.apps.error_handling.decorators import handle_error
from portal.apps.user_messages.api.viewsets import UserMessageViewSet
from portal.apps.user_messages.models import AerpawUserMessage
from portal.server.settings import DEBUG, REST_FRAMEWORK


@csrf_exempt
@login_required
@handle_error
def user_message_list(request):
    message = None
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        if request.method == 'POST':
            if request.POST.get('delete_user_message'):
                um_api_request = Request(request=HttpRequest())
                um_api_request.user = request.user
                um_api_request.method = 'DELETE'
                um = UserMessageViewSet(request=um_api_request)
                for user_message_id in request.POST.getlist('message-checkbox'):
                    um.destroy(request=um_api_request, pk=int(user_message_id))

            if request.POST.get('mark_unread_user_message'):
                for user_message_id in request.POST.getlist('message-checkbox'):
                    user_message_obj = get_object_or_404(AerpawUserMessage, pk=int(user_message_id))
                    user_message_obj.is_read = False
                    user_message_obj.modified_by = request.user.username
                    user_message_obj.save()
            if request.POST.get('mark_read_user_message'):
                for user_message_id in request.POST.getlist('message-checkbox'):
                    user_message_obj = get_object_or_404(AerpawUserMessage, pk=int(user_message_id))
                    user_message_obj.is_read = True
                    user_message_obj.read_date = datetime.now(timezone.utc)
                    user_message_obj.modified_by = request.user.username
                    user_message_obj.save()
        data_dict = {'user_id': request.user.id, 'show_read': True}
        if request.GET.get('page'):
            data_dict['page'] = request.GET.get('page')
            current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        um = UserMessageViewSet(request=request)
        user_messages = um.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if user_messages.data:
            user_messages = dict(user_messages.data)
            prev_url = user_messages.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    catch_exception(exc, request=request)
                    prev_page = 1
            next_url = user_messages.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    catch_exception(exc, request=request)
                    next_page = 1
            count = int(user_messages.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count
        else:
            user_messages = {}
        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        error = catch_exception(exc, request=request)
        message = error.message
        user_messages = {}
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'user_message_list.html',
                  {
                      'user': request.user,
                      'user_messages': user_messages,
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
@handle_error
def user_message_detail(request, user_message_id):
    message = None
    user_message_obj = get_object_or_404(AerpawUserMessage, pk=user_message_id)
    try:
        user_message_obj.is_read = True
        user_message_obj.read_date = datetime.now(timezone.utc)
        user_message_obj.save()
        um = UserMessageViewSet(request=request)
        user_message = um.retrieve(request=request, pk=user_message_id).data
    except Exception as exc:
        error = catch_exception(exc, request=request)
        message = error.message
        user_message = None
    return render(request,
                  'user_message_detail.html',
                  {
                      'user': request.user,
                      'user_message': user_message,
                      'message': message,
                      'debug': DEBUG
                  })

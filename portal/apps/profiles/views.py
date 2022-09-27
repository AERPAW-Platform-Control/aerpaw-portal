from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.request import Request

from portal.apps.credentials.api.viewsets import CredentialViewSet
from portal.apps.users.api.viewsets import UserViewSet
from portal.server.download_utils import download_db_credential_public_key, download_db_user_tokens
from portal.server.settings import DEBUG


@csrf_exempt
@login_required
def profile(request):
    """
    :param request:
    :return:
    """
    message = None
    user = request.user
    api_request = Request(request=HttpRequest())
    user_data = UserViewSet(request=api_request)
    api_request.user = request.user
    api_request.method = 'GET'
    if request.method == 'POST':
        print(request.POST)
        try:
            if request.POST.get('display_name'):
                request.data = {'display_name': request.POST.get('display_name')}
                user_data.update(request, pk=user.id)
            if request.POST.get('generate_tokens'):
                api_request.query_params.update({'generate': 'true'})
            if request.POST.get('refresh_access_token'):
                api_request.query_params.update({'refresh': 'true'})
            if request.POST.get('download_credential'):
                try:
                    response = download_db_credential_public_key(
                        user_id=user.id, credential_id=int(request.POST.get('download_credential'))
                    )
                    return response
                except Exception as exc:
                    message = exc
            if request.POST.get('delete_credential'):
                c_api_request = Request(request=HttpRequest())
                c = CredentialViewSet(request=c_api_request)
                c_api_request.user = request.user
                c_api_request.method = 'DELETE'
                c.destroy(request=c_api_request, pk=request.POST.get('delete_credential'))
            if request.POST.get('download_tokens'):
                try:
                    response = download_db_user_tokens(user_id=user.id)
                    return response
                except Exception as exc:
                    message = exc
            user_data = UserViewSet(request=api_request)
        except Exception as exc:
            message = exc
    user_tokens = user_data.tokens(request=api_request, pk=request.user.id).data
    return render(request,
                  'profile.html',
                  {
                      'user': user,
                      'user_data': user_data.retrieve(request=request, pk=request.user.id).data,
                      'user_tokens': user_tokens,
                      'user_credentials': user_data.credentials(request=request, pk=request.user.id).data,
                      'message': message,
                      'debug': DEBUG
                  })

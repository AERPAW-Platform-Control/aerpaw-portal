from django.contrib.auth.decorators import login_required
from django.http import Http404, QueryDict
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from portal.apps.credentials.api.viewsets import CredentialViewSet
from portal.apps.credentials.forms import CredentialAddForm, CredentialGenerateForm
from portal.apps.error_handling.api.error_utils import catch_exception
from portal.apps.error_handling.decorators import handle_error
from portal.server.download_utils import download_db_credential_private_key, download_db_credential_public_key
from portal.server.settings import DEBUG


@csrf_exempt
@login_required
@handle_error
def credential_create(request):
    message = None
    
    if request.method == "POST":
        if request.POST.get('name'):
            form = CredentialGenerateForm(request.POST)
            if form.is_valid():
                try:
                    request.data = QueryDict('', mutable=True)
                    data_dict = form.data.dict()
                    public_key_name = data_dict.get('name', None)
                    if not public_key_name:
                        raise Http404("BadRequest: missing name or public key")
                    data_dict.update({'public_key_name': public_key_name})
                    request.data.update(data_dict)
                    c = CredentialViewSet(request=request)
                    credential = c.create(request=request).data
                    message = 'OneTimeAccess: Private Key will no longer be available after leaving this page'
                    return render(request,
                                  'credential_download.html',
                                  {
                                      'credential': credential,
                                      'message': message,
                                      'debug': DEBUG
                                  })
                except Exception as exc:
                    catch_exception(exc, request=request)
        else:
            form = CredentialGenerateForm()
        if request.POST.get('private_key_credential'):
            try:
                response = download_db_credential_private_key(
                    user_id=request.user.id, private_key=request.POST.get('private_key_credential')
                )
                return response
            except Exception as exc:
                error = catch_exception(exc, request=request)
                message = error.message
        if request.POST.get('public_key_credential'):
            try:
                response = download_db_credential_public_key(
                    user_id=request.user.id, credential_id=int(request.POST.get('public_key_credential'))
                )
                return response
            except Exception as exc:
                error = catch_exception(exc, request=request)
                message = error.message
    else:
        form = CredentialGenerateForm()
    return render(request,
                  'credential_create.html',
                  {
                      'form': form,
                      'message': message
                  })


@csrf_exempt
@login_required
@handle_error
def credential_add(request):
    message = None
    if request.method == "POST":
        form = CredentialAddForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                public_key_name = data_dict.get('name', None)
                public_key_credential = data_dict.get('credential', None)
                if not public_key_name or not public_key_credential:
                    raise Http404("BadRequest: missing name or public key")
                data_dict.update({'public_key_name': public_key_name})
                data_dict.update({'public_key_credential': public_key_credential})
                request.data.update(data_dict)
                c = CredentialViewSet(request=request)
                credential = c.create(request=request)

                return redirect('profile')
            except Exception as exc:
                error = catch_exception(exc, request=request)
                message = error.message
    else:
        form = CredentialAddForm()
    return render(request,
                  'credential_add.html',
                  {
                      'form': form,
                      'message': message
                  })

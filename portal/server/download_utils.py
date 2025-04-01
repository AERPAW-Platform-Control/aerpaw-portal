import json
import mimetypes
import os

import paramiko
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseServerError
from rest_framework.request import Request

from portal.apps.credentials.models import PublicCredentials
from portal.apps.experiments.models import AerpawExperiment, ExperimentFile
from portal.apps.users.api.viewsets import UserViewSet
from portal.apps.users.models import AerpawUser

aerpaw_ops_host = os.getenv('AERPAW_OPS_HOST')
aerpaw_ops_port = os.getenv('AERPAW_OPS_PORT')
aerpaw_ops_user = os.getenv('AERPAW_OPS_USER')
aerpaw_ops_key = paramiko.RSAKey.from_private_key_file(os.getenv('AERPAW_OPS_KEY_FILE'))
_TMP_FILE_PATH = '/tmp/aerpaw_files'


def download_sftp_experiment_file(user_id: int, experiment_id: int, file_id: int):
    try:
        user = AerpawUser.objects.get(id=user_id)
        experiment = AerpawExperiment.objects.get(id=experiment_id)
        file = ExperimentFile.objects.get(id=file_id)
        if not experiment.is_creator(user) and not experiment.is_member(user):
            raise HttpResponseForbidden

        dest_dir_path = _TMP_FILE_PATH + '/{0}'.format(str(user.uuid))
        filename = file.file_location.split('/')[-1]
        dest_file_path = dest_dir_path + '/{0}'.format(filename)
        print(dest_file_path)

        # create directory /tmp/aerpaw_files/{experiment_uuid:uuid}/filename
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)

        # remove previous file if it already exists
        if os.path.exists(dest_file_path):
            os.remove(dest_file_path)

        try:
            transport = paramiko.Transport(aerpaw_ops_host, int(aerpaw_ops_port))
            transport.connect(username=aerpaw_ops_user, pkey=aerpaw_ops_key)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(file.file_location, dest_file_path)
        except Exception as exc:
            raise HttpResponseServerError
        finally:
            transport.close()

        # download file to user
        mime_type, _ = mimetypes.guess_type(dest_file_path)
        if os.path.exists(dest_file_path):
            with open(dest_file_path, 'r') as fh:
                data = fh.read()
            response = HttpResponse(data, content_type=mime_type)
            response.headers['Content-Length'] = str(len(data.encode('utf-8')))
            response.headers['Content-Disposition'] = "attachment; filename=%s" % filename
            return response
    except Exception as exc:
        raise Http404("FileNotFound: file_id '{0}' not found".format(file_id))


def download_db_credential_public_key(user_id: int, credential_id: int):
    try:
        user = AerpawUser.objects.get(id=user_id)
        credential = PublicCredentials.objects.get(id=credential_id)
        if credential.owner != user:
            raise HttpResponseForbidden

        dest_dir_path = _TMP_FILE_PATH + '/{0}'.format(str(user.uuid))
        filename = 'aerpaw_id_rsa.pub'
        dest_file_path = dest_dir_path + '/{0}'.format(filename)

        # create directory /tmp/aerpaw_files/{user_uuid:uuid}/filename
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)

        # remove previous file if it already exists
        if os.path.exists(dest_file_path):
            os.remove(dest_file_path)

        # write contents of object to file
        with open(dest_file_path, 'w+') as fh:
            fh.writelines(credential.public_credential)

        # download file to user
        mime_type, _ = mimetypes.guess_type(dest_file_path)
        if os.path.exists(dest_file_path):
            with open(dest_file_path, 'r') as fh:
                data = fh.read()
            response = HttpResponse(data, content_type=mime_type)
            response.headers['Content-Length'] = str(len(data.encode('utf-8')))
            response.headers['Content-Disposition'] = "attachment; filename=%s" % filename
            return response
    except Exception as exc:
        raise Http404("FileNotFound: credential_id '{0}' not found".format(credential_id))


def download_db_credential_private_key(user_id: int, private_key: str):
    try:
        user = AerpawUser.objects.get(id=user_id)
        if not private_key:
            raise Http404("FileNotFound: private key not found")

        dest_dir_path = _TMP_FILE_PATH + '/{0}'.format(str(user.uuid))
        filename = 'aerpaw_id_rsa'
        dest_file_path = dest_dir_path + '/{0}'.format(filename)

        # create directory /tmp/aerpaw_files/{user_uuid:uuid}/filename
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)

        # remove previous file if it already exists
        if os.path.exists(dest_file_path):
            os.remove(dest_file_path)

        # write contents of object to file
        with open(dest_file_path, 'w+') as fh:
            fh.writelines(private_key)

        # download file to user
        # mime_type, _ = mimetypes.guess_type(dest_file_path)
        mime_type = 'application/octet-stream'
        if os.path.exists(dest_file_path):
            with open(dest_file_path, 'r') as fh:
                data = fh.read()
            response = HttpResponse(data, content_type=mime_type)
            response.headers['Content-Length'] = str(len(data.encode('utf-8')))
            response.headers['Content-Disposition'] = "attachment; filename=%s" % filename
            return response
    except Exception as exc:
        raise Http404("FileNotFound: private key not found")


def download_db_user_tokens(user_id: int):
    try:
        user = AerpawUser.objects.get(id=user_id)
        api_request = Request(request=HttpRequest())
        user_data = UserViewSet(request=api_request)
        api_request.user = user
        api_request.method = 'GET'
        user_tokens = user_data.tokens(request=api_request, pk=user.id).data

        dest_dir_path = _TMP_FILE_PATH + '/{0}'.format(str(user.uuid))
        filename = 'aerpaw_tokens.json'
        dest_file_path = dest_dir_path + '/{0}'.format(filename)

        # create directory /tmp/aerpaw_files/{user_uuid:uuid}/filename
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)

        # remove previous file if it already exists
        if os.path.exists(dest_file_path):
            os.remove(dest_file_path)

        # write contents of object to file
        with open(dest_file_path, 'w+') as fh:
            fh.writelines(json.dumps(user_tokens, indent=2))

        # download file to user
        mime_type, _ = mimetypes.guess_type(dest_file_path)
        if os.path.exists(dest_file_path):
            with open(dest_file_path, 'r') as fh:
                data = fh.read()
            response = HttpResponse(data, content_type=mime_type)
            response.headers['Content-Length'] = str(len(data.encode('utf-8')))
            response.headers['Content-Disposition'] = "attachment; filename=%s" % filename
            return response
    except Exception as exc:
        raise Http404("FileNotFound: user_id '{0}' not found".format(user_id))

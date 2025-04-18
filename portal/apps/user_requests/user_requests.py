from django.contrib.auth.models import Group

from portal.apps.error_handling.api.error_utils import catch_exception
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.users.models import AerpawRolesEnum


def approve_user_role_request(request_id: int) -> bool:
    user_request = AerpawUserRequest.objects.filter(id=request_id).first()
    user = user_request.requested_by
    if user_request:
        try:
            group_name = None
            # check for experimenter
            if '[{0}]'.format(AerpawRolesEnum.EXPERIMENTER.value) in user_request.request_note:
                group_name = AerpawRolesEnum.EXPERIMENTER.value
            # check for pi
            if '[{0}]'.format(AerpawRolesEnum.PI.value) in user_request.request_note:
                group_name = AerpawRolesEnum.PI.value
            group = Group.objects.filter(name=group_name).first()
            # if group exists and user is not already a member add user to group
            if group:
                if group_name not in [g.name for g in user_request.requested_by.groups.all()]:
                    user = user
                    user.groups.add(group)
                    user.save()
                    return True
                else:
                    return True
            else:
                return False
        except Exception as exc:
            catch_exception(exc, request=None, user=user)
            return False
    else:
        return False


def deny_user_role_request(request_id: int) -> bool:
    user_request = AerpawUserRequest.objects.filter(id=request_id).first()
    user = user_request.requested_by
    if user_request:
        try:
            group_name = None
            # check for experimenter
            if '[{0}]'.format(AerpawRolesEnum.EXPERIMENTER.value) in user_request.request_note:
                group_name = AerpawRolesEnum.EXPERIMENTER.value
            # check for pi
            if '[{0}]'.format(AerpawRolesEnum.PI.value) in user_request.request_note:
                group_name = AerpawRolesEnum.PI.value
            group = Group.objects.filter(name=group_name).first()
            # if group exists and user is not already a member add user to group
            if group:
                if group_name in [g.name for g in user_request.requested_by.groups.all()]:
                    user = user
                    user.groups.remove(group)
                    user.save()
                    return True
                else:
                    return True
            else:
                return False
        except Exception as exc:
            catch_exception(exc, request=None, user=user)
            return False
    else:
        return False


def approve_project_join_request(request_id: int) -> bool:
    # TODO: placeholder for member / owner logic or other checks
    user_request = AerpawUserRequest.objects.filter(id=request_id).first()
    if user_request:
        return True
    else:
        return False


def deny_project_join_request(request_id: int) -> bool:
    # TODO: placeholder for member / owner logic or other checks
    user_request = AerpawUserRequest.objects.filter(id=request_id).first()
    if user_request:
        return True
    else:
        return False


def approve_experiment_join_request(request_id: int) -> bool:
    # TODO: placeholder for member logic or other checks
    user_request = AerpawUserRequest.objects.filter(id=request_id).first()
    if user_request:
        return True
    else:
        return False


def deny_experiment_join_request(request_id: int) -> bool:
    # TODO: placeholder for member logic or other checks
    user_request = AerpawUserRequest.objects.filter(id=request_id).first()
    if user_request:
        return True
    else:
        return False

from django import template

from portal.apps.experiments.models import AerpawExperiment
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.users.models import AerpawUser

register = template.Library()


@register.filter
def pending_experimenter_request(user_id):
    try:
        role_request = AerpawUserRequest.objects.filter(
            request_type=AerpawUserRequest.RequestType.ROLE.value,
            request_type_id=user_id,
            request_note__contains='[experimenter]',
            completed_by=None
        ).first()
        if role_request:
            return role_request.created
        else:
            return None
    except Exception as exc:
        print(exc)
        return None


@register.filter
def pending_pi_request(user_id):
    try:
        role_request = AerpawUserRequest.objects.filter(
            request_type=AerpawUserRequest.RequestType.ROLE.value,
            request_type_id=user_id,
            request_note__contains='[pi]',
            completed_by=None
        ).first()
        if role_request:
            return role_request.created
        else:
            return None
    except Exception as exc:
        print(exc)
        return None


@register.filter
def pending_join_project_request(project_id, user_id):
    try:
        role_request = AerpawUserRequest.objects.filter(
            requested_by__id=user_id,
            request_type=AerpawUserRequest.RequestType.PROJECT.value,
            request_type_id=project_id,
            completed_by=None
        ).first()
        if role_request:
            return role_request.created
        else:
            return None
    except Exception as exc:
        print(exc)
        return None


@register.filter
def pending_join_experiment_request(experiment_id, user_id):
    try:
        role_request = AerpawUserRequest.objects.filter(
            requested_by__id=user_id,
            request_type=AerpawUserRequest.RequestType.EXPERIMENT.value,
            request_type_id=experiment_id,
            completed_by=None
        ).first()
        if role_request:
            return role_request.created
        else:
            return None
    except Exception as exc:
        print(exc)
        return None


@register.filter
def is_experiment_project_member(experiment_id, user_id) -> bool:
    try:
        experiment = AerpawExperiment.objects.filter(
            id=experiment_id
        ).first()
        project = experiment.project
        user = AerpawUser.objects.filter(
            id=user_id
        ).first()
        if project.is_creator(user) or project.is_owner(user) or project.is_member(user):
            return True
        else:
            return False
    except Exception as exc:
        print(exc)
        return False

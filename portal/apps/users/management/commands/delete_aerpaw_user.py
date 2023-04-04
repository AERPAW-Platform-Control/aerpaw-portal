import datetime
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from portal.apps.credentials.models import PublicCredentials
from portal.apps.experiments.models import AerpawExperiment, UserExperiment
from portal.apps.profiles.models import AerpawUserProfile
from portal.apps.projects.models import AerpawProject, UserProject
from portal.apps.resources.models import AerpawResource
from portal.apps.user_messages.models import AerpawUserMessage
from portal.apps.user_requests.models import AerpawUserRequest
from portal.apps.users.models import AerpawUser


def remove_from_experiments(user: AerpawUser, sub_user: AerpawUser):
    """
    remove user from experiment
    - substitute user for experiment: creator, created_by, and modified_by
    - remove user membership
    - substitute user for session: created_by, modified_by, started_by, and ended_by
    """
    # remove user from experiments
    print('### EXPERIMENTS ###')
    try:
        experiments = AerpawExperiment.objects.filter(
            Q(experiment_creator=user) |
            Q(experiment_membership__in=[user]) |
            Q(modified_by=user.email)
        ).distinct()
        for e in experiments:
            print(' - exp: {0} <-- sub/remove user info'.format(e.uuid))
            # experiment creator, created_by, modified_by
            if e.experiment_creator == user:
                e.experiment_creator = sub_user
                e.created_by = sub_user.email
                e.modified_by = sub_user.email
            if e.modified_by == user.email:
                e.modified_by = sub_user.email
            e.save()
            # experiment membership
            try:
                membership = UserExperiment.objects.get(
                    experiment__id=e.id, user__id=user.id
                )
                membership.delete()
            except Exception as exc:
                print(exc)
            # experiment sessions
            sessions = e.session_experiment.all()
            for s in sessions:
                print(' - ses: {0} <-- sub user info'.format(s.uuid))
                if s.created_by == user.email:
                    s.created_by = sub_user.email
                if s.modified_by == user.email:
                    s.modified_by = sub_user.email
                if s.started_by == user:
                    s.started_by = sub_user
                if s.ended_by == user:
                    s.ended_by = sub_user
                s.save()
    except Exception as exc:
        print(exc)


def remove_from_projects(user: AerpawUser, sub_user: AerpawUser):
    """
    remove user from experiment
    - substitute user for project: creator, created_by, and modified_by
    - remove user membership
    """
    # remove user from projects
    print('### PROJECTS ###')
    try:
        projects = AerpawProject.objects.filter(
            Q(project_creator=user) |
            Q(project_membership__in=[user])
        ).distinct()
        for p in projects:
            print(' - prj: {0} <-- sub/remove user info'.format(p.uuid))
            # project creator, created_by, modified_by
            if p.project_creator == user:
                p.project_creator = sub_user
                p.created_by = sub_user.email
                p.modified_by = sub_user.email
            if p.modified_by == user.email:
                p.modified_by = sub_user.email
            p.save()
            # project membership
            membership = UserProject.objects.filter(
                project__id=p.id, user__id=user.id
            ).distinct()
            for m in membership:
                m.delete()
    except Exception as exc:
        print(exc)


def remove_from_user_messages(user: AerpawUser, sub_user: AerpawUser):
    """
    remove user from user_messages
    - delete sent_by messages
    - remove user from received_by messages
    - delete owned_by messages
    """
    # remove user messages
    print('### USER MESSAGES ###')
    try:
        user_messages = AerpawUserMessage.objects.filter(
            Q(message_owner=user) |
            Q(received_by__in=[user]) |
            Q(sent_by=user)
        ).distinct()
        for m in user_messages:
            # delete sent_by messages
            if m.sent_by == user:
                print(' - msg: {0} <-- delete sent_by messages'.format(m.uuid))
                for u in m.received_by.all():
                    m.received_by.remove(u)
                m.delete()
                continue
            # update received_by messages
            if user in m.received_by.all():
                print(' - msg: {0} <-- remove from received_by messages'.format(m.uuid))
                append_msg = '[UPDATE] {0} - user removed from system: {1}'.format(datetime.now(tz=timezone.utc),
                                                                                   user.display_name)
                m.message_body = m.message_body + '\r\n' + append_msg
                m.received_by.remove(user)
                m.save()
            # delete owned_by messages
            if m.message_owner == user:
                print(' - msg: {0} <-- delete owned_by messages'.format(m.uuid))
                for u in m.received_by.all():
                    m.received_by.remove(u)
                m.delete()
    except Exception as exc:
        print(exc)


def remove_from_user_requests(user: AerpawUser, sub_user: AerpawUser):
    """
    remove user from user_requests
    - delete requested_by requests
    - remove user from received_by requests
    - substitute user in completed_by requests
    """
    # remove user requests
    print('### USER REQUESTS ###')
    try:
        user_requests = AerpawUserRequest.objects.filter(
            Q(requested_by=user) |
            Q(received_by__in=[user]) |
            Q(completed_by=user)
        ).distinct()
        for r in user_requests:
            if r.requested_by == user:
                print(' - req: {0} <-- delete requested_by requests'.format(r.uuid))
                for u in r.received_by.all():
                    r.received_by.remove(u)
                r.delete()
                continue
            if user in r.received_by.all():
                print(' - req: {0} <-- remove from received_by requests'.format(r.uuid))
                append_msg = '[UPDATE] {0} - user removed from system: {1}'.format(datetime.now(tz=timezone.utc),
                                                                                   user.display_name)
                r.response_note = r.response_note + '\r\n' + append_msg
                r.received_by.remove(user)
                r.save()
            if r.completed_by == user:
                print(' - req: {0} <-- substitute completed_by requests'.format(r.uuid))
                r.completed_by = sub_user
                r.save()
    except Exception as exc:
        print(exc)


def remove_from_groups(user: AerpawUser, sub_user: AerpawUser):
    """
    remove user from groups
    - delete all user.groups associations
    """
    # remove user groups
    print('### USER GROUPS ###')
    try:
        for g in user.groups.all():
            print(' - grp: {0} <-- remove from group'.format(g.name))
            user.groups.remove(g)
        user.save()
    except Exception as exc:
        print(exc)


def remove_from_profiles(user: AerpawUser, sub_user: AerpawUser):
    """
    remove profile from user account
    - remove profile from user
    - delete profile
    """
    # remove user profile
    print('### USER PROFILE ###')
    try:
        user_profile = AerpawUserProfile.objects.get(pk=user.profile_id)
        print(' - prof: {0} <-- remove profile'.format(user_profile.uuid))
        user.profile = None
        user.save()
        user_profile.delete()
    except Exception as exc:
        print(exc)


def remove_from_resources(user: AerpawUser, sub_user: AerpawUser):
    """
    remove user from resources
    - substitute user with sub_user
    """
    # change user ownership of resources if they created any
    print('### OWNED RESOURCES ###')
    try:
        resources = AerpawResource.objects.filter(
            Q(created_by=user.username) | Q(modified_by=user.username)
        ).distinct()
        now = datetime.now(tz=timezone.utc)
        for r in resources:
            print(' - resc: {0} <-- substitute created_by'.format(r.uuid))
            r.created_by = sub_user.username
            r.modified_by = sub_user.username
            r.modified = now
            r.save()
    except Exception as exc:
        print(exc)


def remove_from_credentials(user: AerpawUser, sub_user: AerpawUser):
    """
    remove all user credentials
    """
    print('### CREDENTIALS ###')
    try:
        credentials = PublicCredentials.objects.filter(owner=user)
        for c in credentials:
            print(' - cred: {0} <-- delete credential'.format(c.uuid))
            c.delete()
    except Exception as exc:
        print(exc)


def delete_aerpaw_user(user_id, substitute_user_id):
    """
    Delete aerpaw user from all database tables
    """
    try:
        # verify user_id and substitute_user_id
        print('### USER INFO ###')
        user = AerpawUser.objects.get(pk=user_id)
        sub_user = AerpawUser.objects.get(pk=substitute_user_id)
        print(' - name:', user.display_name, '<-- user to remove')
        print(' - name:', sub_user.display_name, '<-- substitute user')
        remove_from_experiments(user=user, sub_user=sub_user)
        remove_from_projects(user=user, sub_user=sub_user)
        remove_from_user_messages(user=user, sub_user=sub_user)
        remove_from_user_requests(user=user, sub_user=sub_user)
        remove_from_groups(user=user, sub_user=sub_user)
        remove_from_profiles(user=user, sub_user=sub_user)
        remove_from_resources(user=user, sub_user=sub_user)
        remove_from_credentials(user=user, sub_user=sub_user)
        # remove user
        print('### DELETE USER ###')
        print(' - user: {0} <-- delete user'.format(user.uuid))
        try:
            user.delete()
        except Exception as exc:
            print(exc)
    except Exception as e:
        print(e)


class Command(BaseCommand):
    help = 'Delete AERPAW user from all database tables'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int)
        parser.add_argument('substitute_user_id', type=int)

    def handle(self, *args, **kwargs):
        try:
            delete_aerpaw_user(user_id=kwargs['user_id'], substitute_user_id=kwargs['substitute_user_id'])

        except Exception as e:
            print(e)
            raise CommandError('Initialization failed.')

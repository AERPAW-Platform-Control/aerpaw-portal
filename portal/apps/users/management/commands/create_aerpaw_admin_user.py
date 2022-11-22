import os

from django.core.management.base import BaseCommand, CommandError

from portal.apps.users.oidc_users import MyOIDCAB


def create_aerpaw_admin_user():
    """
    Create and return a `User` with superuser (admin) permissions.

    Must provide a subset of the "claims" to mimic those normally received from CILogon for create_user
    {
        'sub': 'http://cilogon.org/serverA/users/00000000',  <-- mock value required by create_user
        'given_name': 'AERPAW',                              <-- modify from admin panel
        'family_name': 'Admin',                              <-- modify from admin panel
        'email': 'aerpaw@gmail.com',                         <-- AERPAW_OPS_PORTAL_USERNAME environment variable
    }
    """
    try:
        password = os.getenv('AERPAW_OPS_PORTAL_PASSWORD')
        claims = {
            'sub': 'http://cilogon.org/serverA/users/00000000',
            'given_name': 'AERPAW',
            'family_name': 'Admin',
            'email': os.getenv('AERPAW_OPS_PORTAL_USERNAME'),
        }
        create_superuser = MyOIDCAB()
        user = create_superuser.create_user(claims)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
    except Exception as e:
        print(e)


class Command(BaseCommand):
    help = 'Set node_display_name if NULL'

    def handle(self, *args, **kwargs):
        try:
            create_aerpaw_admin_user()

        except Exception as e:
            print(e)
            raise CommandError('Initialization failed.')

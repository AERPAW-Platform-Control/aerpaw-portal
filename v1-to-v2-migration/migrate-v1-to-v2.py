"""
Migration portal v1 to portal v2

v1 Roles                            v2 Roles
pk_v1   name                        pk_v2   name
------------------------            --------------------
1       site_admin          -->     4       site_admin
2       operator            -->     3       operator
3       project_manager     -->     2       pi
4       resource_manager    -->     N/A
5       aerpaw_user         -->     1       experimenter
6       user_manager        -->     N/A

"""

import ast
import json
from datetime import datetime, timedelta, timezone
from itertools import count
from uuid import uuid4
from dateutil import parser

# globals

INPUT_DIR = 'v1-data/dumpdata'
OUTPUT_DIR = 'v2-data/fixtures'
CREDENTIAL_EXPIRY_DAYS = 365

with open(INPUT_DIR + '/resources.json', 'r') as f:
    v1_resources = json.load(f)
with open(INPUT_DIR + '/profiles.json', 'r') as f:
    v1_profiles = json.load(f)
v2_canonical_number_pk = count(1)
v2_cer_pk = count(1)
v2_cers = []
v2_credentials = []
v2_credential_pk = count(1)
v2_experiment_files = []
v2_experiments = []
v2_operations = []
v2_profiles = []
v2_projects = []
v2_projects_personnel_pk = count(1)
v2_resources = []
v2_user_messages = []
v2_user_requests = []
v2_users = []


def credentials(v2_user: dict, publickey: str):
    """
    Imported from v1.accounts.aerpawuser and output as:
    - credentials.publiccredentials
      - name - unknown at import time and set to: username + " publickey"

    output: v2 credentials.json
    {
      "model": "credentials.publiccredentials",
      "pk": 1,
      "fields": {
        "created": "2022-08-11T13:19:03.437Z",
        "modified": "2022-08-11T19:24:49.469Z",
        "created_by": "stealey@unc.edu",
        "modified_by": "stealey@unc.edu",
        "expiry_date": "2022-08-11T19:24:49.469Z",
        "is_deleted": true,
        "name": "stealey demo key",
        "owner": 1,
        "public_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD...AJoOT2svnkeWKcBsP1f6BCymVCZ9gBoJDBYwry9",
        "uuid": "d641cef8-bd70-443e-9345-ee8c5d6d32d2"
      }
    }
    """
    v2_credential = {
        'model': 'credentials.publiccredentials',
        'pk': next(v2_credential_pk),
        'fields': {
            'created': normalize_date_format(v2_user.get('fields').get('created')),
            'modified': normalize_date_format(v2_user.get('fields').get('modified')),
            'created_by': v2_user.get('fields').get('username'),
            'modified_by': v2_user.get('fields').get('username'),
            'expiry_date': normalize_date_format(str((datetime.now(timezone.utc) + timedelta(days=CREDENTIAL_EXPIRY_DAYS)).strftime(
                '%Y-%m-%dT%H:%M:%S.000Z'))),
            'is_deleted': True if str(v2_user.get('fields').get('created')).casefold() == 'true' else False,
            'name': v2_user.get('fields').get('username') + ' publickey',
            'owner': v2_user.get('pk'),
            'public_credential': publickey,
            'uuid': str(uuid4())
        }
    }
    v2_credentials.append(v2_credential)
    # print(json.dumps(v2_credential, indent=2))


def experiment_files():
    """
    experiments.json
    """
    pass


def experiments():
    """
    Imported from v1 experiments.experiment and output as:
    - v2 experiments.aerpawexperiment
    - experiment_files - not added

    output: v2 experiment_files.json
    {
      "model": "experiments.aerpawexperiment",
      "pk": 4,
      "fields": {
        "created": "2022-08-22T17:14:52.864Z",
        "modified": "2022-11-07T04:27:43.208Z",
        "created_by": "snagara9@ncsu.edu",
        "modified_by": "snagara9@ncsu.edu",
        "canonical_number": 4,
        "description": "Test Exp 4",
        "experiment_creator": 7,
        "experiment_flags": "000",
        "experiment_state": "saved",
        "is_canonical": true,
        "is_deleted": false,
        "is_emulation_required": true,
        "is_retired": false,
        "name": "Exp_4",
        "project": 4,
        "resources_locked": true,
        "uuid": "1a03cba3-1fbc-4a9d-84c2-bc9af3e30659",
        "experiment_files": [
          60,
          61
        ],
        "resources": [
          4,
          1
        ]
      }
    },
    {
      "model": "experiments.userexperiment",
      "pk": 19,
      "fields": {
        "experiment": 10,
        "granted_by": 7,
        "granted_date": "2022-08-26T05:58:53.086Z",
        "user": 5
      }
    },
    {
      "model": "experiments.canonicalexperimentresource",
      "pk": 6,
      "fields": {
        "created": "2022-08-23T18:11:20.952Z",
        "modified": "2022-10-17T17:22:36.269Z",
        "experiment": 4,
        "experiment_node_number": 1,
        "node_display_name": "CC1",
        "node_type": "afrn",
        "node_uhd": "1.3.3",
        "node_vehicle": "vehicle_none",
        "resource": 1,
        "uuid": ""
      }
    }
    
    input: v1 experiments.json
    {
      "model": "experiments.experiment",
      "pk": 86,
      "fields": {
        "uuid": "0a078d89-3a51-4e32-9246-781d9eb0f82a",
        "name": "Test 1",
        "description": "Testing existing experiments",
        "project": 36,
        "created_by": 70,
        "created_date": "2022-05-25T14:00:51.678Z",
        "modified_by": 22,
        "modified_date": "2022-07-04T18:12:05.991Z",
        "stage": "Development",
        "profile": 56,
        "is_snapshotted": false,
        "state": 3,
        "deployment_bn": null,
        "message": "{'ap_msg_type': 'experiment_development_session_notification', 'session_type': 'Development' ...",
        "submit_notes": "",
        "experimenter": [
          57,
          102,
          103
        ]
      }
    }
    """
    with open(INPUT_DIR + '/experiments.json', 'r') as f:
        v1_experiments = json.load(f)
    experiment_personnel = []
    for e_v1 in v1_experiments:
        if e_v1.get('model') == 'experiments.experiment':
            # get v2 canonical number - operations()
            canonical_number = operations(v1_experiment=e_v1)
            # get resource ids and set canonical experiment resources
            e_v2_resources = get_v2_experiment_resources_from_v1(v1_experiment=e_v1)
            print('Exp_ID: ' + str(e_v1.get('pk')) + ', resources: ' + str(e_v2_resources))
            e_v2 = {
                'model': 'experiments.aerpawexperiment',
                'pk': e_v1.get('pk'),
                'fields': {
                    'created': normalize_date_format(e_v1.get('fields').get('created_date')),
                    'modified': normalize_date_format(e_v1.get('fields').get('modified_date')),
                    'created_by': get_v2_username_from_id(user_id=e_v1.get('fields').get('created_by')),
                    'modified_by': get_v2_username_from_id(user_id=e_v1.get('fields').get('modified_by')),
                    'canonical_number': canonical_number,
                    'description': e_v1.get('fields').get('description'),
                    'experiment_creator': e_v1.get('fields').get('created_by'),
                    'experiment_flags': '000',
                    'experiment_state': 'saved',
                    'is_canonical': True,
                    'is_deleted': False,
                    'is_emulation_required': True,
                    'is_retired': False,
                    'name': e_v1.get('fields').get('name'),
                    'project': e_v1.get('fields').get('project'),
                    'resources_locked': False,
                    'uuid': e_v1.get('fields').get('uuid'),
                    'experiment_files': [],
                    'resources': e_v2_resources
                }
            }
            v2_experiments.append(e_v2)
            # print(json.dumps(e_v2, indent=2))

            # collect experiment personnel
            # experiment_members
            for p in e_v1.get('fields').get('experimenter'):
                em = {
                    'model': 'experiments.userexperiment',
                    'pk': next(v2_projects_personnel_pk),
                    'fields': {
                        'experiment': e_v1.get('pk'),
                        'granted_by': e_v1.get('fields').get('created_by'),
                        'granted_date': normalize_date_format(e_v1.get('fields').get('created_date')),
                        'user': p
                    }
                }
                experiment_personnel.append(em)
                # print(json.dumps(em, indent=2))

    # append experiment_personnel to bottom of experiments.json fixture
    for p in experiment_personnel:
        v2_experiments.append(p)

    # append canonical experiment resources to bottom of experiments.json fixture
    for cer in v2_cers:
        v2_experiments.append(cer)


def operations(v1_experiment: dict):
    """
    output: v2 operations.json
    {
      "model": "operations.canonicalnumber",
      "pk": 4,
      "fields": {
        "created": "2022-08-22T17:14:52.863Z",
        "modified": "2022-08-22T17:14:52.863Z",
        "canonical_number": 4,
        "is_deleted": false,
        "is_retired": false
      }
    }

    input: v1 experiment
    {
      "model": "experiments.experiment",
      "pk": 86,
      "fields": {
        "uuid": "0a078d89-3a51-4e32-9246-781d9eb0f82a",
        "name": "Test 1",
        "description": "Testing existing experiments",
        "project": 36,
        "created_by": 70,
        "created_date": "2022-05-25T14:00:51.678Z",
        "modified_by": 22,
        "modified_date": "2022-07-04T18:12:05.991Z",
        "stage": "Development",
        "profile": 56,
        "is_snapshotted": false,
        "state": 3,
        "deployment_bn": null,
        "message": "{'ap_msg_type': 'experiment_development_session_notification', 'session_type': 'Development' ...",
        "submit_notes": "",
        "experimenter": [
          57,
          102,
          103
        ]
      }
    }
    """
    canonical_number_pk = next(v2_canonical_number_pk)
    v2_canonical_number = {
        'model': 'operations.canonicalnumber',
        'pk': canonical_number_pk,
        'fields': {
            'created': normalize_date_format(v1_experiment.get('fields').get('created_date')),
            'modified': normalize_date_format(v1_experiment.get('fields').get('modified_date')),
            'canonical_number': v1_experiment.get('pk'),
            'is_deleted': False,
            'is_retired': False
        }
    }
    v2_operations.append(v2_canonical_number)
    return canonical_number_pk


def profiles(v2_user: dict):
    """
    Imported from v1.accounts.aerpawuser and output as:
    - profiles.aerpawuserprofile
      - employer - unknown at import time and set to None
      - position - unknown at import time and set to None
      - research_field - unknown at import time and set to None

    output: v2 profiles.json
    {
      "model": "profiles.aerpawuserprofile",
      "pk": 1,
      "fields": {
        "created": "2022-07-14T14:29:24.423Z",
        "modified": "2022-12-01T01:24:14.764Z",
        "created_by": "stealey@unc.edu",
        "modified_by": "stealey@unc.edu",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...0RF92qNWmRIVQW_76Pr2BkkkJHmQ6m9rS6agyCntiZc",
        "employer": "RENCI - UNC Chapel Hill",
        "position": "Distributed Systems Software Engineer",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...8YQl5YJxE6w4TBWFgdZZskzGZfYhhl2nrzW-0uRoRz0",
        "research_field": null,
        "uuid": "1047126b-9301-440f-b8e3-9978c15206c4"
      }
    }
    """
    v2_profile = {
        'model': 'profiles.aerpawuserprofile',
        'pk': v2_user.get('pk'),
        'fields': {
            'created': normalize_date_format(v2_user.get('fields').get('created')),
            'modified': normalize_date_format(v2_user.get('fields').get('modified')),
            'created_by': v2_user.get('fields').get('username'),
            'modified_by': v2_user.get('fields').get('username'),
            'access_token': None,
            'employer': None,
            'position': None,
            'refresh_token': None,
            'research_field': None,
            'uuid': str(uuid4())
        }
    }
    v2_profiles.append(v2_profile)
    # print(json.dumps(v2_profile, indent=2))


def projects():
    """
    projects.json

    output: v2 projects.json
    {
      "model": "projects.aerpawproject",
      "pk": 4,
      "fields": {
        "created": "2022-08-22T17:09:49.683Z",
        "modified": "2022-08-22T17:09:49.683Z",
        "created_by": "snagara9@ncsu.edu",
        "modified_by": "snagara9@ncsu.edu",
        "description": "Sudhanva dummy project",
        "is_deleted": false,
        "is_public": false,
        "name": "snagara9_test_project",
        "project_creator": 7,
        "uuid": "b93a3936-afb1-4411-af20-60771fafb3e1"
      }
    }
    {
      "model": "projects.userproject",
      "pk": 10,
      "fields": {
        "granted_by": 7,
        "granted_date": "2022-08-22T17:09:49.686Z",
        "project": 4,
        "project_role": "project_owner",
        "user": 7
      }
    },
    {
      "model": "projects.userproject",
      "pk": 11,
      "fields": {
        "granted_by": 7,
        "granted_date": "2022-08-23T18:08:59.767Z",
        "project": 4,
        "project_role": "project_member",
        "user": 2
      }
    }

    input: v1 projects.json
    {
      "model": "projects.project",
      "pk": 18,
      "fields": {
        "name": "Beta Testing",
        "description": "Beta test of experiment development ...",
        "uuid": "1727f4db-1d59-459f-8eac-4baf7ae508e0",
        "is_public": false,
        "project_creator": 24,
        "created_by": 24,
        "created_date": "2021-09-22T14:45:10.376Z",
        "modified_by": 24,
        "modified_date": "2021-09-22T17:17:09.979Z",
        "project_owners": [
          19,
          24
        ],
        "project_members": [
          24,
          19
        ]
      }
    }
    """
    with open(INPUT_DIR + '/projects.json', 'r') as f:
        v1_projects = json.load(f)
    project_personnel = []
    for p_v1 in v1_projects:
        # create projects.aerpawproject fixture
        if p_v1.get('model') == 'projects.project':
            p_v2 = {
                'model': 'projects.aerpawproject',
                'pk': p_v1.get('pk'),
                'fields': {
                    'created': normalize_date_format(p_v1.get('fields').get('created_date')),
                    'modified': normalize_date_format(p_v1.get('fields').get('modified_date')),
                    'created_by': get_v2_username_from_id(user_id=p_v1.get('fields').get('created_by')),
                    'modified_by': get_v2_username_from_id(user_id=p_v1.get('fields').get('modified_by')),
                    'description': p_v1.get('fields').get('description'),
                    'is_deleted': False,
                    'is_public': True if str(p_v1.get('fields').get('is_public')).casefold() == 'true' else False,
                    'name': p_v1.get('fields').get('name'),
                    'project_creator': p_v1.get('fields').get('created_by'),
                    'uuid': p_v1.get('fields').get('uuid')
                }
            }
            v2_projects.append(p_v2)
            # print(json.dumps(p_v2, indent=2))

            # collect project_personnel
            # project_owners
            for p in p_v1.get('fields').get('project_owners'):
                po = {
                    'model': 'projects.userproject',
                    'pk': next(v2_projects_personnel_pk),
                    'fields': {
                        'granted_by': p_v1.get('fields').get('created_by'),
                        'granted_date': normalize_date_format(p_v1.get('fields').get('created_date')),
                        'project': p_v1.get('pk'),
                        'project_role': 'project_owner',
                        'user': p
                    }
                }
                project_personnel.append(po)
                # print(json.dumps(po, indent=2))
            for p in p_v1.get('fields').get('project_members'):
                pm = {
                    'model': 'projects.userproject',
                    'pk': next(v2_projects_personnel_pk),
                    'fields': {
                        'granted_by': p_v1.get('fields').get('created_by'),
                        'granted_date': normalize_date_format(p_v1.get('fields').get('created_date')),
                        'project': p_v1.get('pk'),
                        'project_role': 'project_member',
                        'user': p
                    }
                }
                project_personnel.append(pm)
                # print(json.dumps(pm, indent=2))

    # append project_personnel to bottom of projects.json fixture
    for p in project_personnel:
        v2_projects.append(p)


def resources():
    """
    Import from v1 resources.resource will affect the following in v2:
    - resources.aerpawresource
    - default to user_id = 11 when NULL - which is Rudra

    output: v2 resources.json
    {
      "model": "resources.aerpawresource",
      "pk": 1,
      "fields": {
        "created": "2022-07-20T20:06:22.244Z",
        "modified": "2022-10-26T23:39:25.844Z",
        "created_by": "stealey@unc.edu",
        "modified_by": "snagara9@ncsu.edu",
        "description": "Centennial Campus Node 1",
        "hostname": "aerpaw18",
        "ip_address": "152.14.188.101",
        "is_active": true,
        "is_deleted": false,
        "location": "Centennial Campus",
        "name": "CC1",
        "ops_notes": "",
        "resource_class": "allow_canonical",
        "resource_mode": "testbed",
        "resource_type": "AFRN",
        "uuid": "151e8890-0b71-4520-b8da-afc2a2ea3133"
      }
    }

    input: v1 resources.json
    {
      "model": "resources.resource",
      "pk": 2,
      "fields": {
        "admin": 11,
        "uuid": "2dcc723a-aca2-4013-8a97-2f6bde09f588",
        "name": "CC1",
        "description": "Centennial Campus Node 1",
        "resourceType": "FixedNode",
        "units": 1,
        "availableUnits": 1,
        "location": "Centennial",
        "stage": "Testbed",
        "created_date": "2021-07-08T19:55:36Z",
        "ip_address": "152.14.188.118",
        "hostname": "aerpaw18"
      }
    }
    """
    for r_v1 in v1_resources:
        created_by = get_v2_username_from_id(user_id=r_v1.get('fields').get('admin'))
        if not created_by:
            created_by = get_v2_username_from_id(user_id=11)
        resource_type = 'AFRN' if r_v1.get('fields').get('resourceType') == 'FixedNode' else 'APRN'
        r_v2 = {
            'model': 'resources.aerpawresource',
            'pk': r_v1.get('pk'),
            'fields': {
                'created': normalize_date_format(r_v1.get('fields').get('created_date')),
                'modified': normalize_date_format(r_v1.get('fields').get('created_date')),
                'created_by': created_by,
                'modified_by': created_by,
                'description': r_v1.get('fields').get('description'),
                'hostname': r_v1.get('fields').get('hostname'),
                'ip_address': r_v1.get('fields').get('ip_address'),
                'is_active': True,
                'is_deleted': False,
                'location': 'Centennial Campus',
                'name': r_v1.get('fields').get('name'),
                'ops_notes': None,
                'resource_class': 'allow_canonical',
                'resource_mode': 'testbed',
                'resource_type': resource_type,
                'uuid': r_v1.get('fields').get('uuid')
            }
        }
        v2_resources.append(r_v2)
    # add two copies of the UAV resource to account for experiments with multiples
    r_pk = count(max([r.get('pk') for r in v2_resources]) + 1)
    for r in v2_resources:
        if r.get('pk') == 4:
            # add copy 1
            copy_1 = r.copy()
            copy_1['pk'] = next(r_pk)
            v2_resources.append(copy_1)
            # copy 2
            copy_2 = r.copy()
            copy_2['pk'] = next(r_pk)
            v2_resources.append(copy_2)
    for r in v2_resources:
        print('Resource_ID: ' + str(r.get('pk')) + ', name: ' + r.get('fields').get('name') +
              ' - ' + r.get('fields').get('resource_type') + ' - ' + r.get('fields').get('description'))


def user_messages():
    """
    user_messages.json
    """
    pass


def user_requests():
    """
    user_requests.json
    """
    pass


def users():
    """
    Import from v1.accounts.aerpawuser will affect the following in v2:
    - users.aerpawuser
    - profiles.aerpawuserprofile
    - credentials.publiccredentials

    output: users.json
    {
      "model": "users.aerpawuser",
      "pk": 1,
      "fields": {
        "password": "",
        "last_login": "2022-12-12T20:03:22.882Z",
        "is_superuser": true,
        "username": "stealey@unc.edu",
        "first_name": "Michael",
        "last_name": "Stealey",
        "email": "stealey@unc.edu",
        "is_staff": true,
        "is_active": true,
        "date_joined": "2022-07-14T14:29:24Z",
        "created": "2022-07-14T14:29:24.421Z",
        "modified": "2022-12-12T20:03:22.873Z",
        "created_by": "stealey@unc.edu",
        "modified_by": "stealey@unc.edu",
        "display_name": "Michael J. Stealey",
        "openid_sub": "http://cilogon.org/serverA/users/242181",
        "profile": 1,
        "uuid": "5376cc65-9d98-4f98-b192-210973f753e2",
        "groups": [
          1,
          2,
          3,
          4
        ],
        "user_permissions": []
      }
    }

    input: accounts.json
    {
      "model": "accounts.aerpawuser",
      "pk": 1,
      "fields": {
        "password": "pbkdf2_sha256...AwP6rbaWbds=",
        "last_login": "2021-12-10T12:53:41.423Z",
        "is_superuser": true,
        "username": "admin",
        "first_name": "aerpaw",
        "last_name": "ncsu",
        "email": "aerpaw@gmail.com",
        "is_staff": true,
        "is_active": true,
        "date_joined": "2021-07-01T17:21:34Z",
        "uuid": "8a20fa7a-26e4-4cb0-a610-e1ba61f3a678",
        "display_name": "AERPAW Admin",
        "oidc_claim_sub": "http://cilogon.org/serverA/users/51476771",
        "oidc_claim_iss": "https://cilogon.org",
        "oidc_claim_aud": "cilogon:/client_id/20e53848eb61b99a99a8efdd439ec2e1",
        "oidc_claim_token_id": "https://cilogon.org/oauth2/idToken/...",
        "oidc_claim_email": "aerpaw@gmail.com",
        "oidc_claim_given_name": "aerpaw",
        "oidc_claim_family_name": "ncsu",
        "oidc_claim_name": "aerpaw ncsu",
        "oidc_claim_idp": "http://google.com/accounts/o8/id",
        "oidc_claim_idp_name": "Google",
        "oidc_claim_eppn": "",
        "oidc_claim_eptid": "",
        "oidc_claim_affiliation": "",
        "oidc_claim_ou": "",
        "oidc_claim_oidc": "105612366609870937821",
        "oidc_claim_cert_subject_dn": "/DC=org/DC=cilogon/C=US/O=Google/CN=aerpaw ncsu A51476771",
        "oidc_claim_acr": "",
        "oidc_claim_entitlement": "",
        "publickey": null,
        "groups": [
          1,
          2,
          3,
          4,
          5,
          6
        ],
        "user_permissions": []
      }
    }
    """
    with open(INPUT_DIR + '/accounts.json', 'r') as f:
        v1_accounts = json.load(f)
    for u_v1 in v1_accounts:
        if u_v1.get('model') == 'accounts.aerpawuser':
            # create users.aerpawuser fixture
            v1_groups = u_v1.get('fields').get('groups')
            v2_groups = []
            if 1 in v1_groups:
                v2_groups.append(4)
            if 2 in v1_groups:
                v2_groups.append(3)
            if 3 in v1_groups:
                v2_groups.append(2)
            if 5 in v1_groups:
                v2_groups.append(1)

            u_v2 = {
                'model': 'users.aerpawuser',
                'pk': u_v1.get('pk'),
                'fields': {
                    'password': '',
                    'last_login': normalize_date_format(u_v1.get('fields').get('last_login')),
                    'is_superuser': True if str(u_v1.get('fields').get('is_superuser')).casefold() == 'true' else False,
                    'username': u_v1.get('fields').get('username'),
                    'first_name': u_v1.get('fields').get('first_name'),
                    'last_name': u_v1.get('fields').get('last_name'),
                    'email': u_v1.get('fields').get('email'),
                    'is_staff': True if str(u_v1.get('fields').get('is_staff')).casefold() == 'true' else False,
                    'is_active': True if str(u_v1.get('fields').get('is_active')).casefold() == 'true' else False,
                    'date_joined': normalize_date_format(u_v1.get('fields').get('date_joined')),
                    'created': normalize_date_format(u_v1.get('fields').get('date_joined')),
                    'modified': normalize_date_format(str(datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z'))),
                    'created_by': u_v1.get('fields').get('email'),
                    'modified_by': u_v1.get('fields').get('email'),
                    'display_name': u_v1.get('fields').get('display_name'),
                    'openid_sub': u_v1.get('fields').get('oidc_claim_sub'),
                    'profile': u_v1.get('pk'),
                    'uuid': u_v1.get('fields').get('uuid'),
                    'groups': v2_groups,
                    'user_permissions': []
                }
            }
            v2_users.append(u_v2)
            # create profiles.aerpawuserprofile
            profiles(u_v2)
            # create credentials.publiccredentials
            if u_v1.get('fields').get('publickey'):
                credentials(u_v2, publickey=u_v1.get('fields').get('publickey'))

            # print(json.dumps(v2_users, indent=2))


def get_v2_username_from_id(user_id: int) -> str:
    try:
        result = [u.get('fields').get('username') for u in v2_users if u.get('pk') == user_id]
        return result[0]
    except Exception as exc:
        print(exc)
        return ''


def get_v1_resource_id_by_node(node: dict) -> int:
    try:
        component_id = node.get('component_id', None)
        hardware_type = node.get('hardware_type', None)
        vehicle = node.get('vehicle', None)
        result = [r.get('pk') for r in v1_resources if
                  r.get('fields').get('name') in [component_id, vehicle]
                  and r.get('fields').get('resourceType') == hardware_type]
        return result[0]
    except Exception as exc:
        print(exc)
        return 0


def get_v2_experiment_resources_from_v1(v1_experiment: dict) -> [dict]:
    """
    output: v2 canonical experiment resource
    {
      "model": "experiments.canonicalexperimentresource",
      "pk": 24,
      "fields": {
        "created": "2022-09-29T18:55:23.453Z",
        "modified": "2022-10-17T17:22:36.313Z",
        "experiment": 11,
        "experiment_node_number": 1,
        "node_display_name": "CC2",
        "node_type": "afrn",
        "node_uhd": "1.3.3",
        "node_vehicle": "vehicle_none",
        "resource": 2,
        "uuid": ""
      }
    }

    input: v1 profile
    {
      "model": "profiles.profile",
      "pk": 56,
      "fields": {
        "uuid": "1663843b-827a-46da-90e4-76d5856a6f63",
        "name": "Lake Wheeler 1P+1F (copy)",
        "description": "Simple scenario for Lake Wheeler with one portable node (PN1) on an UAV and one fixed node (LW1)",
        "is_template": false,
        "project": 36,
        "profile": "[{\"idx\": 1, \"name\": \"portablenode1\", \"hardware_type\": \"PortableNode\", \"vehicle\": \"UAV\", \"uhd_ver\": \"4.0\" },{\"idx\":2, \"name\": \"'fixednode1\", \"hardware_type\": \"FixedNode\", \"component_id\": \"LW1\", \"uhd_ver\": \"4.0\" }]",
        "created_by": 70,
        "created_date": "2022-05-25T14:00:51.675Z",
        "modified_by": 70,
        "modified_date": "2022-05-25T14:00:51.675Z",
        "stage": ""
      }
    }
    """
    # print('----------------------------------')
    # print('experiment_id: ' + str(v1_experiment.get('pk')))
    v2_resource_ids = []
    v1_profile = [p for p in v1_profiles if p.get('pk') == v1_experiment.get('fields').get('profile')]
    nodes_json = v1_profile[0].get('fields').get('profile')
    nodes = ast.literal_eval(nodes_json)
    for node in nodes:
        # print(get_v1_resource_id_by_node(node=node))
        if node.get('vehicle') == 'UAV':
            node_vehicle = 'vehicle_uav'
        elif node.get('vehicle') == 'UGV':
            node_vehicle = 'vehicle_ugv'
        else:
            node_vehicle = 'vehicle_none'
        resource = get_v1_resource_id_by_node(node=node)
        # adjust for multiple UAV entries
        if resource in v2_resource_ids and resource == 4:
            resource = 7
        if resource in v2_resource_ids and resource == 7:
            resource = 8
        v2_cer = {
            'model': 'experiments.canonicalexperimentresource',
            'pk': next(v2_cer_pk),
            'fields': {
                'created': normalize_date_format(v1_experiment.get('fields').get('created_date')),
                'modified': normalize_date_format(v1_experiment.get('fields').get('modified_date')),
                'experiment': v1_experiment.get('pk'),
                'experiment_node_number': node.get('idx'),
                'node_display_name': node.get('name'),
                'node_type': 'afrn' if node.get('hardware_type') == 'FixedNode' else 'aprn',
                'node_uhd': '1.3.3' if node.get('uhd_ver') == '3.1.5' else '1.4.0',
                'node_vehicle': node_vehicle,
                'resource': resource,
                'uuid': str(uuid4())
            }
        }
        v2_resource_ids.append(resource)
        v2_cers.append(v2_cer)
        # print(json.dumps(v2_cer, indent=2))
        # print(json.dumps(node, indent=2))
    return v2_resource_ids


def normalize_date_format(v1_date: str):
    v2_date = parser.parse(v1_date) + timedelta(milliseconds=100)
    # print(v2_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z"))
    return v2_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z")


def output_fixture_files():
    """
    Output v2 fixture files
    """
    if v2_credentials:
        with open(OUTPUT_DIR + '/credentials.json', 'w') as f:
            f.write(json.dumps(v2_credentials, indent=2))
    if v2_experiments:
        with open(OUTPUT_DIR + '/experiments.json', 'w') as f:
            f.write(json.dumps(v2_experiments, indent=2))
    if v2_operations:
        with open(OUTPUT_DIR + '/operations.json', 'w') as f:
            f.write(json.dumps(v2_operations, indent=2))
    if v2_profiles:
        with open(OUTPUT_DIR + '/profiles.json', 'w') as f:
            f.write(json.dumps(v2_profiles, indent=2))
    if v2_projects:
        with open(OUTPUT_DIR + '/projects.json', 'w') as f:
            f.write(json.dumps(v2_projects, indent=2))
    if v2_resources:
        with open(OUTPUT_DIR + '/resources.json', 'w') as f:
            f.write(json.dumps(v2_resources, indent=2))
    if v2_users:
        with open(OUTPUT_DIR + '/users.json', 'w') as f:
            f.write(json.dumps(v2_users, indent=2))


if __name__ == '__main__':
    users()
    resources()
    projects()
    experiments()
    output_fixture_files()

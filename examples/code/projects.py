""" examples/code/users.py

Examples:
    - /projects: paginated list with search, create new project
    - /projects/{int:pk}: detail for single project, update single project
    - /projects/{int:pk}/experiments: list of project experiments
    - /projects/{int:pk}/membership: list of project membership, edit project membership

"""
import json

from config import api_session as api, API_URL

# data below was populated knowing that Users exist for ID 1 and 3
project_data = {
    'name': 'example code project',
    'description': 'example code project description',
    'is_public': False
}
updated_project_data = {
    'description': 'updated example code project description',
    'is_public': True
}
project_membership = {
    "project_members": [1, 3],
    "project_owners": [1, 3]
}

"""
GET /projects

- all projects as paginated list
- search for "stea" in name or email
"""
print('')
print('*** /projects: paginated list with search***')

# all projects
API_CALL = API_URL + '/projects'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

# search for "stea" in name
API_CALL = API_URL + '/projects?search=stea'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /projects/{int:pk}

- details for project with pk = 2
"""
print('')
print('*** /projects/{int:pk}: detail for single project ***')
API_CALL = API_URL + '/projects/2'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /projects/{int:pk}/experiments

- experiments for project with pk = 2
"""
print('')
print('*** /projects/{int:pk}/experiments: list of project experiments ***')
API_CALL = API_URL + '/projects/2/experiments'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /projects/{int:pk}/membership

- membership for project with pk = 2
"""
print('')
print('*** /projects/{int:pk}/membership: list of project membership, edit project membership ***')
API_CALL = API_URL + '/projects/2/membership'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
*** NOTE ***
Running code in the following sections will generate a new project and add project members to it
"""

"""
POST /projects

- create new project
"""
print('')
print('*** /projects: create new project***')
API_CALL = API_URL + '/projects'
data = json.dumps(project_data)
response = api.post(API_CALL, data=data)
python_object = json.loads(response.text)
print('*** POST: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))
project_id = python_object.get('project_id')

"""
PUT /projects/{int:pk}

- update single project with pk = project_id
"""
print('')
print('*** /projects/{int:pk}: update existing project ***')
API_CALL = API_URL + '/projects/' + str(project_id)
data = json.dumps(updated_project_data)
response = api.put(API_CALL, data=data)
python_object = json.loads(response.text)
print('*** PUT: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
PUT /projects/{int:pk}/membership

- update project_members and project_owners for a single project with pk = project_id
"""
print('')
print('*** /projects/{int:pk}/membership: update project membership ***')
API_CALL = API_URL + '/projects/' + str(project_id) + '/membership'
data = json.dumps(project_membership)
response = api.put(API_CALL, data=data)
python_object = json.loads(response.text)
print('*** PUT: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /projects/{int:pk}

- details for project with pk = project_id
"""
print('')
print('*** /projects/{int:pk}: detail for single project ***')
API_CALL = API_URL + '/projects/' + str(project_id)
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
file: examples/code/projects.py

Examples:
- /projects: paginated list of projects (GET)
- /projects: create a new project (POST)
- /projects?search=string: paginated list of projects with search (GET)
- /projects/{int:pk}: retrieve single project (GET)
- /projects/{int:pk}: update single project (PUT)
- /projects/{int:pk}/experiments: list of project experiments (GET)
- /projects/{int:pk}/membership: list of project membership (GET)
- /projects/{int:pk}/membership: edit project membership (PUT)
- /projects/{int:pk}: soft delete a single project (DELETE)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global resource id for examples
project_id = 0


def get_projects_list():
    """
    GET /projects
    - paginated list of projects
    """
    api_call = API_URL + '/projects'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def post_projects_create():
    """
    POST /resources
    - create new resource
    - data = {
        "description": "string",
        "is_public": boolean,
        "name": "string"
      }
    """
    api_call = API_URL + '/projects'
    data = json.dumps(
        {
            'description': 'demo project for testing purposes',
            'is_public': True,
            'name': 'demo project'
        }
    )
    response = api.post(api_call, data=data)
    print_json_output(
        about='*** POST: {0} ***'.format(api_call),
        payload=response
    )
    # capture resource_id of newly created resource - use subsequent examples
    global project_id
    project_id = json.loads(response.text).get('project_id')


def get_projects_list_search():
    """
    GET /projects?search=string
    - paginated list of projects with search for term "demo"
    """
    api_call = API_URL + '/projects?search=demo'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_projects_detail():
    """
    GET /projects/{int:pk}
    - details for project with pk = project_id
    """
    api_call = API_URL + '/projects/{0}'.format(project_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def put_projects_detail():
    """
    PUT /projects/{int:pk}
    - update single project with pk = project_id
    - data = {
        "description": "string",
        "is_public": boolean,
        "name": "string"
      }
    """
    api_call = API_URL + '/projects/{0}'.format(project_id)
    data = json.dumps(
        {
            'description': 'demo project for testing purposes - updated',
            'is_public': False,
        }
    )
    response = api.put(api_call, data=data)
    print_json_output(
        about='*** PUT: {0} ***'.format(api_call),
        payload=response
    )


def get_projects_detail_experiments():
    """
    GET /projects/{int:pk}/experiments
    - experiments for project with pk = project_id
    """
    api_call = API_URL + '/projects/{0}/experiments'.format(project_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_projects_detail_membership():
    """
    GET /projects/{int:pk}/membership
    - membership for project with pk = project_id
    """
    api_call = API_URL + '/projects/{0}/membership'.format(project_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def put_projects_detail_membership():
    """
    PUT /projects/{int:pk}/membership
    - update project_members and project_owners for a single project with pk = project_id
    - data = {
        "project_members": [ int ],
        "project_owners": [ int ]
      }
    """
    api_call = API_URL + '/projects/' + str(project_id) + '/membership'
    data = json.dumps(
        {
            'project_members': [12],
            'project_owners': [11, 22]
        }
    )
    response = api.put(api_call, data=data)
    print_json_output(
        about='*** PUT: {0} ***'.format(api_call),
        payload=response
    )


def delete_projects_detail():
    """
    DELETE /projects/{int:pk}
    - delete project with pk = project_id
    """
    api_call = API_URL + '/projects/{0}'.format(project_id)
    response = api.delete(api_call)
    print_json_output(
        about='*** DELETE: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_projects_list()
    post_projects_create()
    get_projects_list_search()
    get_projects_detail()
    put_projects_detail()
    get_projects_detail_experiments()
    get_projects_detail_membership()
    put_projects_detail_membership()
    get_projects_detail()
    delete_projects_detail()

"""
file: examples/code/resources.py

Examples:
- /resources: paginated list of resources (GET)
- /resources: create a new resource (POST)
- /resources?search=string: paginated list of resources with search (GET)
- /resources/{int:pk}: retrieve single resource (GET)
- /resources/{int:pk}: update single resource (PUT)
- /resources/{int:pk}/experiments: list of user credentials (GET)
- /resources/{int:pk}/projects: retrieve user profile (GET)
- /resources/{int:pk}: soft delete a single resource (DELETE)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global resource id for examples
resource_id = 0


def get_resources_list():
    """
    GET /resources
    - paginated list of resources
    """
    api_call = API_URL + '/resources'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def post_resources_create():
    """
    POST /resources
    - create new resource
    - data = {
            "description": "string",
            "hostname": "string",
            "ip_address": "string",
            "is_active": boolean,
            "location": "string",
            "name": "string",
            "ops_notes": "string",
            "resource_class": "string",
            "resource_mode": "string",
            "resource_type": "string"
        }
    """
    api_call = API_URL + '/resources'
    data = json.dumps(
        {
            'description': 'demo resource for testing purposes',
            'hostname': 'demo.resource.org',
            'ip_address': '213.213.213.213',
            'is_active': True,
            'location': 'in the demo area',
            'name': 'demo resource',
            'ops_notes': 'this resource should be good to go',
            'resource_class': 'allow_canonical',
            'resource_mode': 'testbed',
            'resource_type': 'AFRN'
        }
    )
    response = api.post(api_call, data=data)
    print_json_output(
        about='*** POST: {0} ***'.format(api_call),
        payload=response
    )
    # capture resource_id of newly created resource - use subsequent examples
    global resource_id
    resource_id = json.loads(response.text).get('resource_id')


def get_resources_list_search():
    """
    GET /resources?search=string
    - paginated list of resources with search for term "afrn"
    """
    api_call = API_URL + '/resources?search=afrn'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_resources_detail():
    """
    GET /resources/{int:pk}
    - retrieve details for resource with pk = resource_id
    """
    api_call = API_URL + '/resources/{0}'.format(resource_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def put_resources_detail():
    """
    PUT /resources/{int:pk}
    - update "display_name" for user with pk = resource_id
    - data = {"ops_notes": "string"}
    """
    api_call = API_URL + '/resources/{0}'.format(resource_id)
    data = json.dumps(
        {'ops_notes': 'update IP Address to be 123.123.123.123 on 12/12/2023'}
    )
    response = api.put(api_call, data=data)
    print_json_output(
        about='*** PUT: {0} ***'.format(api_call),
        payload=response
    )


# TODO: add resource-experiments to resources API calls
def get_resources_detail_experiments():
    """
    GET /resources/{int:pk}/experiments
    - retrieve list of experiments targeting resource = {int:pk}
    """
    api_call = API_URL + '/resources/2/experiments'
    response = api.get(api_call)
    print_json_output(
        about='*** TODO: GET: {0} ***'.format(api_call),
        payload=response
    )


# TODO: add resource-projects to resources API calls
def get_resources_detail_projects():
    """
    GET /resources/{int:pk}/projects
    - retrieve list of projects targeting resource = {int:pk}
    """
    api_call = API_URL + '/resources/2/projects'
    response = api.get(api_call)
    print_json_output(
        about='*** TODO: GET: {0} ***'.format(api_call),
        payload=response
    )


def delete_resources_detail():
    """
    DELETE /resources/{int:pk}
    - delete resource with pk = resource_id
    """
    api_call = API_URL + '/resources/{0}'.format(resource_id)
    response = api.delete(api_call)
    print_json_output(
        about='*** DELETE: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_resources_list()
    post_resources_create()
    get_resources_list_search()
    get_resources_detail()
    put_resources_detail()
    get_resources_detail_experiments()
    get_resources_detail_projects()
    delete_resources_detail()

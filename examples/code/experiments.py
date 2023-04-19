"""
file: examples/code/experiments.py

Examples:
- /experiments: paginated list of experiments (GET)
- /experiments: create a new experiment (POST)
- /experiments?search=string: paginated list of experiments with search (GET)
- /experiments/{int:pk}: retrieve single experiment (GET)
- /experiments/{int:pk}: update single experiment (PUT)
- /experiments/{int:pk}/experiments: list of experiment experiments (GET)
- /experiments/{int:pk}/membership: list of experiment membership (GET)
- /experiments/{int:pk}/membership: edit experiment membership (PUT)
- /experiments/{int:pk}: soft delete a single experiment (DELETE)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global resource id for examples
experiment_id = 108
project_id = 39


def get_experiments_list():
    """
    GET /experiments
    - paginated list of experiments
    """
    api_call = API_URL + '/experiments'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def post_experiments_create():
    """
    POST /resources
    - create new resource
    - data = {
        "description": "string",
        "name": "string",
        "project_id": integer
      }
    """
    api_call = API_URL + '/experiments'
    data = json.dumps(
        {
            'description': 'demo_code experiment for testing purposes',
            'name': 'demo_code experiment',
            'project_id': project_id
        }
    )
    response = api.post(api_call, data=data)
    print_json_output(
        about='*** POST: {0} ***'.format(api_call),
        payload=response
    )
    # capture resource_id of newly created resource - use subsequent examples
    global experiment_id
    experiment_id = json.loads(response.text).get('experiment_id')
    print(experiment_id)


def get_experiments_list_search():
    """
    GET /experiments?search=string
    - paginated list of experiments with search for term "demo"
    """
    api_call = API_URL + '/experiments?search=demo_code'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_experiments_detail():
    """
    GET /experiments/{int:pk}
    - details for experiment with pk = experiment_id
    """
    api_call = API_URL + '/experiments/{0}'.format(experiment_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def put_experiments_detail():
    """
    PUT /experiments/{int:pk}
    - update single experiment with pk = experiment_id
    - data = {
        "description": "string",
        "is_retired": boolean,
        "name": "string"
      }
    """
    api_call = API_URL + '/experiments/{0}'.format(experiment_id)
    data = json.dumps(
        {
            'description': 'demo_code experiment for testing purposes - updated',
            'is_retired': False,
        }
    )
    response = api.put(api_call, data=data)
    print_json_output(
        about='*** PUT: {0} ***'.format(api_call),
        payload=response
    )


def get_experiments_detail_experiments():
    """
    GET /experiments/{int:pk}/experiments
    - experiments for experiment with pk = experiment_id
    """
    api_call = API_URL + '/experiments/{0}/experiments'.format(experiment_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_experiments_detail_membership():
    """
    GET /experiments/{int:pk}/membership
    - membership for experiment with pk = experiment_id
    """
    api_call = API_URL + '/experiments/{0}/membership'.format(experiment_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def put_experiments_detail_membership():
    """
    PUT /experiments/{int:pk}/membership
    - update experiment_members and experiment_owners for a single experiment with pk = experiment_id
    - data = {
        "experiment_members": [ int ],
        "experiment_owners": [ int ]
      }
    """
    api_call = API_URL + '/experiments/' + str(experiment_id) + '/membership'
    data = json.dumps(
        {
            'experiment_members': [12],
            'experiment_owners': [11, 22]
        }
    )
    response = api.put(api_call, data=data)
    print_json_output(
        about='*** PUT: {0} ***'.format(api_call),
        payload=response
    )


def delete_experiments_detail():
    """
    DELETE /experiments/{int:pk}
    - delete experiment with pk = experiment_id
    """
    api_call = API_URL + '/experiments/{0}'.format(experiment_id)
    response = api.delete(api_call)
    print_json_output(
        about='*** DELETE: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_experiments_list()
    post_experiments_create()
    get_experiments_list_search()
    get_experiments_detail()
    put_experiments_detail()
    get_experiments_detail_experiments()
    get_experiments_detail_membership()
    put_experiments_detail_membership()
    get_experiments_detail()
    # delete_experiments_detail()

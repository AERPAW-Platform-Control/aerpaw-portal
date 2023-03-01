"""
file: examples/code/canonical_experiment_resource.py

Examples:
- /canonical_experiment_resource: paginated list of canonical_experiment_resource (GET)
- /canonical_experiment_resource?resource_id=int: paginated list of canonical_experiment_resource
  with search by resource_id (GET)
- /canonical_experiment_resource/{int:pk}: retrieve single canonical_experiment_resource (GET)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global canonical_experiment_resource id for examples
canonical_experiment_resource_id = 0


def get_canonical_experiment_resource_list():
    """
    GET /canonical_experiment_resource
    - paginated list of canonical_experiment_resource
    """
    api_call = API_URL + '/canonical-experiment-resource'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_canonical_experiment_resource_list_search():
    """
    GET /canonical_experiment_resource?resource_id=int
    - paginated list of canonical_experiment_resource with search by resource_id = <int>
    """
    api_call = API_URL + '/canonical-experiment-resource?resource_id=5'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )
    # capture canonical_experiment_resource_id of first canonical_experiment_resource
    global canonical_experiment_resource_id
    canonical_experiment_resource_id = json.loads(response.text).get('results')[0].get(
        'canonical_experiment_resource_id')


def get_canonical_experiment_resource_detail():
    """
    GET /canonical_experiment_resource/{int:pk}
    - details for canonical_experiment_resource with pk = canonical_experiment_resource_id
    """
    api_call = API_URL + '/canonical-experiment-resource/{0}'.format(canonical_experiment_resource_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_canonical_experiment_resource_list()
    get_canonical_experiment_resource_list_search()
    get_canonical_experiment_resource_detail()

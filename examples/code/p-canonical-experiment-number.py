"""
file: examples/code/p_canonical_experiment_number.py

Examples:
- /p-canonical-experiment-number: paginated list of canonical experiment numbers ordered by most recent first (GET)
- /p-canonical-experiment-number/{int:pk}: details for single canonical experiment number with pk = canonical_number_id (GET)
- /p-canonical-experiment-number/current: get current canonical experiment number (GET)
- /p_canonical_experiment_number/current?number=int: put new value for current canonical experiment number (PUT)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global variables for examples
canonical_number_id = 0
new_number = 123


def get_p_canonical_experiment_number_list():
    """
    GET /p-canonical-experiment-number
    - paginated list of canonical experiment numbers ordered by most recent first
    """
    api_call = API_URL + '/p-canonical-experiment-number'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )
    # capture canonical_number_id of first message
    global canonical_number_id
    canonical_number_id = json.loads(response.text).get('results')[0].get('canonical_number_id')


def get_p_canonical_experiment_number_detail():
    """
    GET /p-canonical-experiment-number/{int:pk}
    - details for single canonical experiment number with pk = canonical_number_id
    """
    api_call = API_URL + '/p-canonical-experiment-number/{0}'.format(canonical_number_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_p_canonical_experiment_number_current():
    """
    GET /p-canonical-experiment-number/current
    - get current canonical experiment number
    """
    api_call = API_URL + '/p-canonical-experiment-number/current'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def put_p_canonical_experiment_number_current():
    """
    PUT /p_canonical_experiment_number/current?number=int
    - put new value for current canonical experiment number
    """
    api_call = API_URL + '/p-canonical-experiment-number/current?number={0}'.format(new_number)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_p_canonical_experiment_number_list()
    get_p_canonical_experiment_number_detail()
    get_p_canonical_experiment_number_current()
    put_p_canonical_experiment_number_current()

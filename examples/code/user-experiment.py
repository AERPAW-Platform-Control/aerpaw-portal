"""
file: examples/code/user-experiment.py

Examples:
- /user-experiment: paginated list of user-experiment relations (GET)
- /user-experiment?experiment_id=<int>: paginated list of user-experiment relations with search by experiment_id (GET)
- /user-experiment/{int:pk}: retrieve single user-experiment relation (GET)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global resource id for examples
user_experiment_id = 0


def get_user_experiment_list():
    """
    GET /user-experiment
    - paginated list of user-experiment relations
    """
    api_call = API_URL + '/user-experiment'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_user_experiment_list_search():
    """
    GET /user-experiment?search=string
    - paginated list of user-experiment relations where experiment_id = 107
    """
    api_call = API_URL + '/user-experiment?experiment_id=107'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )
    # capture resource_id of newly created resource - use subsequent examples
    global user_experiment_id
    user_experiment_id = json.loads(response.text).get('results')[0].get('id')


def get_user_experiment_detail():
    """
    GET /user-experiment/{int:pk}
    - details for user-experiment with pk = user_experiment_id
    """
    api_call = API_URL + '/user-experiment/{0}'.format(user_experiment_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_user_experiment_list()
    get_user_experiment_list_search()
    get_user_experiment_detail()

"""
file: examples/code/user-project.py

Examples:
- /user-project: paginated list of user-project relations (GET)
- /user-project?project_id=<int>: paginated list of user-project relations with search by project_id (GET)
- /user-project/{int:pk}: retrieve single user-project relation (GET)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global resource id for examples
user_project_id = 0


def get_user_project_list():
    """
    GET /user-project
    - paginated list of user-project relations
    """
    api_call = API_URL + '/user-project'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_user_project_list_search():
    """
    GET /user-project?search=string
    - paginated list of user-project relations where project_id = 27
    """
    api_call = API_URL + '/user-project?project_id=27'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )
    # capture resource_id of newly created resource - use subsequent examples
    global user_project_id
    user_project_id = json.loads(response.text).get('results')[0].get('id')


def get_user_project_detail():
    """
    GET /user-project/{int:pk}
    - details for user-project with pk = user_project_id
    """
    api_call = API_URL + '/user-project/{0}'.format(user_project_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_user_project_list()
    get_user_project_list_search()
    get_user_project_detail()

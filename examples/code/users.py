"""
file: examples/code/users.py

Examples:
- /users: paginated list of users (GET)
- /users?search=string: paginated list of users with search (GET)
- /users/{int:pk}: retrieve single user (GET)
- /users/{int:pk}: update single user display_name (PUT)
- /users/{int:pk}/credentials: list of user credentials (GET)
- /users/{int:pk}/profile: retrieve user profile (GET)
- /users/{int:pk}/tokens: retrieve user tokens (GET)
- /users/{int:pk}/tokens?refresh=true: refresh user tokens (GET)
- /users/{int:pk}/tokens?generate=true: generate user tokens (GET)

"""
import json

from config import api_session as api, API_URL, print_json_output


def get_users_list():
    """
    GET /users
    - paginated list of users
    """
    api_call = API_URL + '/users'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_users_list_search():
    """
    GET /users?search=string
    - paginated list of users with search for term "stea"
    """
    api_call = API_URL + '/users?search=stea'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_users_detail():
    """
    GET /users/{int:pk}
    - retrieve details for user with pk = 2
    """
    api_call = API_URL + '/users/2'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def put_users_detail():
    """
    PUT /users/{int:pk}
    - update "display_name" for user with pk = 2
    - data = {"display_name": "string"}
    """
    api_call = API_URL + '/users/2'
    data = json.dumps(
        {'display_name': 'Michael J. Stealey, Sr.'}
    )
    response = api.put(api_call, data=data)
    print_json_output(
        about='*** PUT: {0} ***'.format(api_call),
        payload=response
    )


def get_users_detail_credentials():
    """
    GET /users/{int:pk}/credentials
    - retrieve credentials for user with pk = 2
    """
    api_call = API_URL + '/users/2/credentials'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_users_detail_profile():
    """
    GET /users/{int:pk}/profile
    - retrieve profile for user with pk = 2
    """
    api_call = API_URL + '/users/2/profile'
    response = api.get(api_call)
    print(response.text)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


# TODO: add user-profile to external API (currently only internal)
def put_users_detail_profile():
    """
    PUT /users/{int:pk}/profile
    - update profile for user with pk = 2
    - data = {"employer": "string", "position": "string", "research_field": "string"}
    """
    api_call = API_URL + '/users/2/profile'
    data = json.dumps(
        {
            'employer': 'UNC Chapel Hill',
            'position': 'Software Engineer',
            'research_field': 'Distributed Systems'
        }
    )
    response = api.put(api_call, data=data)
    print_json_output(
        about='*** TODO: PUT: {0} ***'.format(api_call),
        payload=response
    )


def get_users_detail_tokens():
    """
    GET /users/{int:pk}/tokens
    - retrieve tokens for user with pk = 2
    """
    api_call = API_URL + '/users/2/tokens'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_users_detail_tokens_refresh():
    """
    GET /users/{int:pk}/tokens?refresh=true
    - refresh tokens for user with pk = 2
    """
    api_call = API_URL + '/users/2/tokens?refresh=true'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_users_detail_tokens_generate():
    """
    GET /users/{int:pk}/tokens?generate=true
    - generate tokens for user with pk = 2
    """
    api_call = API_URL + '/users/2/tokens?generate=true'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_users_list()
    get_users_list_search()
    get_users_detail()
    put_users_detail()
    get_users_detail_credentials()
    get_users_detail_profile()
    put_users_detail_profile()
    get_users_detail_tokens()
    get_users_detail_tokens_refresh()
    get_users_detail_tokens_generate()

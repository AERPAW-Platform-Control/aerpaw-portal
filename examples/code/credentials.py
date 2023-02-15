"""
file: examples/code/credentials.py

Examples:
- /credentials: paginated list of credentials (GET)
- /credentials: create a new credential (POST)
- /credentials?user_id=int: paginated list of credentials with search by user_id (GET)
- /credentials/{int:pk}: retrieve single credential (GET)
- /credentials/{int:pk}: update single credential (PUT)
- /credentials/{int:pk}: soft delete a single credential (DELETE)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global resource id for examples
public_key_id = 0


def get_credentials_list():
    """
    GET /credentials
    - paginated list of credentials
    """
    api_call = API_URL + '/credentials'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def post_credentials_create():
    """
    POST /resources
    - create new resource
    - data = {
        "public_key_credential": "<string>"
        "public_key_name": "<string>"
      }
    """
    api_call = API_URL + '/credentials'
    data = json.dumps(
        {
            'public_key_name': 'demo key name for testing purposes'
        }
    )
    response = api.post(api_call, data=data)
    print_json_output(
        about='*** POST: {0} ***'.format(api_call),
        payload=response
    )
    # capture public_key_id of newly created resource - use subsequent examples
    global public_key_id
    public_key_id = json.loads(response.text).get('public_key_id')


def get_credentials_list_search():
    """
    GET /credentials?search=string
    - paginated list of credentials with search by user_id = <int>
    """
    api_call = API_URL + '/credentials?user_id=22'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_credentials_detail():
    """
    GET /credentials/{int:pk}
    - details for credential with pk = public_key_id
    """
    api_call = API_URL + '/credentials/{0}'.format(public_key_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def put_credentials_detail():
    """
    PUT /credentials/{int:pk}
    - update single credential with pk = public_key_id
    - data = {
        "public_key_name": "<string>"
      }
    """
    api_call = API_URL + '/credentials/{0}'.format(public_key_id)
    data = json.dumps(
        {
            'public_key_name': 'update demo key name for testing purposes'
        }
    )
    response = api.put(api_call, data=data)
    print_json_output(
        about='*** PUT: {0} ***'.format(api_call),
        payload=response
    )


def delete_credentials_detail():
    """
    DELETE /credentials/{int:pk}
    - delete credential with pk = public_key_id
    """
    api_call = API_URL + '/credentials/{0}'.format(public_key_id)
    response = api.delete(api_call)
    print_json_output(
        about='*** DELETE: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_credentials_list()
    post_credentials_create()
    get_credentials_list_search()
    get_credentials_detail()
    put_credentials_detail()
    delete_credentials_detail()

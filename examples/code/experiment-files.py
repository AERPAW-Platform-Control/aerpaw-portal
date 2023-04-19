"""
file: examples/code/experiment-files.py

Examples:
- /experiment-files: paginated list of experiment-files (GET)
- /experiment-files: create new experiment-files object (POST)
- /experiment-files?search=<string>: paginated list of experiment-files with text search by name, notes or type (GET)
- /experiment-files/{int:pk}: retrieve single experiment-files object (GET)
- /experiment-files/{int:pk}: update existing single experiment-files object (PUT)
- /experiment-files/{int:pk}: delete existing single experiment-files object (DELETE)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global session id for examples
file_id = 0


def get_experiment_files_list():
    """
    GET /experiment-files
    - paginated list of experiment-files
    """
    api_call = API_URL + '/experiment-files'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )
    # capture session_id of first session
    global file_id
    file_id = json.loads(response.text).get('results')[0].get('file_id')


def post_experiment_files_create():
    """
    POST /experiment-files
    - create new experiment file
    - data = {
        "file_location": "string",
        "file_name": "string",
        "file_notes": "string",
        "file_type": "string" in ["ip_list", "ovpn"]
      }
    """
    api_call = API_URL + '/experiment-files'
    data = json.dumps(
        {
            'file_location': '/home/aerpawops/some/place/to/store/files',
            'file_name': 'manifest-example.txt',
            'file_notes': 'example manifest file for demo purposes',
            'file_type': 'ip_list'
        }
    )
    response = api.post(api_call, data=data)
    print_json_output(
        about='*** POST: {0} ***'.format(api_call),
        payload=response
    )
    # capture session_id of first session
    global file_id
    file_id = json.loads(response.text).get('file_id')


def get_experiment_files_list_search():
    """
    GET /experiment-files?resource_id=int
    - paginated list of experiment files with search by resource_id = <int>
    """
    api_call = API_URL + '/experiment-files?search=example'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_experiment_files_detail():
    """
    GET /experiment-files/{int:pk}
    - details for experiment file with pk = file_id
    """
    api_call = API_URL + '/experiment-files/{0}'.format(file_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def put_experiment_files_detail():
    """
    PUT /experiment-files/{int:pk}
    - update single experiment file with pk = file_id
    - data = {
        "file_location": "string",
        "file_name": "string",
        "file_notes": "string",
        "file_type": "string" in ["ip_list", "ovpn"]
      }
    """
    api_call = API_URL + '/experiment-files/{0}'.format(file_id)
    data = json.dumps(
        {
            'file_name': 'manifest-example-v2.txt',
            'file_notes': 'updated example manifest file for demo purposes'
        }
    )
    response = api.put(api_call, data=data)
    print_json_output(
        about='*** PUT: {0} ***'.format(api_call),
        payload=response
    )


def delete_experiment_files_detail():
    """
    DELETE /experiment-files/{int:pk}
    - delete experiment file with pk = file_id
    """
    api_call = API_URL + '/experiment-files/{0}'.format(file_id)
    response = api.delete(api_call)
    print_json_output(
        about='*** DELETE: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_experiment_files_list()
    post_experiment_files_create()
    get_experiment_files_list_search()
    get_experiment_files_detail()
    put_experiment_files_detail()
    delete_experiment_files_detail()

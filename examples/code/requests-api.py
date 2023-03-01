"""
file: examples/code/requests.py

Examples:
- /requests: paginated list of requests (GET)
- /requests?experiment_id=int: paginated list of requests with search by experiment_id (GET)
- /requests/{int:pk}: retrieve single request (GET)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global request id for examples
request_id = 0


def get_requests_list():
    """
    GET /requests
    - paginated list of requests
    """
    api_call = API_URL + '/requests'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_requests_list_search():
    """
    GET /requests?user_id=int
    - paginated list of requests with search by user_id = <int>
    """
    api_call = API_URL + '/requests?user_id=2&show_completed=true'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )
    # capture request_id of first request
    global request_id
    request_id = json.loads(response.text).get('results')[0].get('request_id')


def get_requests_detail():
    """
    GET /requests/{int:pk}
    - details for request with pk = request_id
    """
    api_call = API_URL + '/requests/{0}'.format(request_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def delete_requests_detail():
    """
    DELETE /requests/{int:pk}
    - remove request with pk = request_id
    """
    api_call = API_URL + '/requests/{0}'.format(request_id)
    response = api.delete(api_call)
    print_json_output(
        about='*** DELETE: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_requests_list()
    get_requests_list_search()
    get_requests_detail()
    # delete_requests_detail()

"""
file: examples/code/sessions.py

Examples:
- /sessions: paginated list of sessions (GET)
- /sessions?experiment_id=int: paginated list of sessions with search by experiment_id (GET)
- /sessions/{int:pk}: retrieve single session (GET)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global session id for examples
session_id = 0


def get_sessions_list():
    """
    GET /sessions
    - paginated list of sessions
    """
    api_call = API_URL + '/sessions'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_sessions_list_search():
    """
    GET /sessions?resource_id=int
    - paginated list of sessions with search by resource_id = <int>
    """
    api_call = API_URL + '/sessions?experiment_id=100'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )
    # capture session_id of first session
    global session_id
    session_id = json.loads(response.text).get('results')[0].get('session_id')


def get_sessions_detail():
    """
    GET /sessions/{int:pk}
    - details for session with pk = session_id
    """
    api_call = API_URL + '/sessions/{0}'.format(session_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_sessions_list()
    get_sessions_list_search()
    get_sessions_detail()

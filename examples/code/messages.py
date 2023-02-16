"""
file: examples/code/messages.py

Examples:
- /messages: paginated list of messages (GET)
- /messages?experiment_id=int: paginated list of messages with search by experiment_id (GET)
- /messages/{int:pk}: retrieve single message (GET)

"""
import json

from config import api_session as api, API_URL, print_json_output

# global message id for examples
message_id = 0


def get_messages_list():
    """
    GET /messages
    - paginated list of messages
    """
    api_call = API_URL + '/messages'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def get_messages_list_search():
    """
    GET /messages?user_id=int
    - paginated list of messages with search by user_id = <int>
    """
    api_call = API_URL + '/messages?user_id=2'
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )
    # capture message_id of first message
    global message_id
    message_id = json.loads(response.text).get('results')[0].get('message_id')


def get_messages_detail():
    """
    GET /messages/{int:pk}
    - details for message with pk = message_id
    """
    api_call = API_URL + '/messages/{0}'.format(message_id)
    response = api.get(api_call)
    print_json_output(
        about='*** GET: {0} ***'.format(api_call),
        payload=response
    )


def delete_messages_detail():
    """
    DELETE /messages/{int:pk}
    - remove message with pk = message_id
    """
    api_call = API_URL + '/messages/{0}'.format(message_id)
    response = api.delete(api_call)
    print_json_output(
        about='*** DELETE: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    get_messages_list()
    get_messages_list_search()
    get_messages_detail()
    delete_messages_detail()

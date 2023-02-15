"""
file: examples/code/token-refresh.py

Examples:
- /token/refresh/: refresh access_token using a valid refresh_token (POST)

"""
import json

from config import api_session as api, API_URL, print_json_output, REFRESH_TOKEN


def post_token_refresh():
    """
    POST /token/refresh/
    - refresh access_token using a valid refresh_token
    """
    api_call = API_URL + '/token/refresh/'
    data = json.dumps(
        {
            'refresh': REFRESH_TOKEN
        }
    )
    response = api.post(api_call, data=data)
    print_json_output(
        about='*** POST: {0} ***'.format(api_call),
        payload=response
    )


if __name__ == '__main__':
    post_token_refresh()

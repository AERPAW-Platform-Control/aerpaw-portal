# configuration to be used by scripts found in examples/code
import json

import requests
import urllib3

# for use with self-signed certificate - suppress warning output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# User to provide appropriate values
API_URL = 'https://127.0.0.1:8443/api'
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...SNDrA-3iaGcAfWLnoXspWLAbRlS5g3l2iApRuZKLfbw'
REFRESH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...b3W3W81cGQACsjsjAcDI8GWUSvSAvxl95cicIXFfD8g'

headers = {
    'Authorization': 'Bearer ' + ACCESS_TOKEN,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

api_session = requests.Session()
api_session.headers = headers
# for use with self-signed certificate - normally verify = True
api_session.verify = False


def print_json_output(about: str, payload):
    if isinstance(payload, requests.Response):
        print(about)
        try:
            payload_dict = json.loads(payload.text)
            print(json.dumps(payload_dict, indent=2))
        except Exception as exc:
            print('- Response: {0}'.format(payload))
    else:
        print('- Response: {0}'.format(payload))
    print('*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*\r\n')

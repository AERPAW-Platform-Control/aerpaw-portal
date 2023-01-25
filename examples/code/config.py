# configuration to be used by scripts found in examples/code
import json

import requests
import urllib3

# for use with self-signed certificate - suppress warning output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# User to provide appropriate values
API_URL = 'https://127.0.0.1:8443/api'
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..izQ3n2ULsXH_JljKY52o6ZnNjw09avmA1abtxA0kJBE'
REFRESH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..R934CGbCDPZAU-kodLVvcWLSQmySFf8x6a36wLjJjc0'

headers = {
    'Authorization': 'Bearer ' + ACCESS_TOKEN,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

api_session = requests.Session()
api_session.headers = headers
# for use with self-signed certificate - normally verify = True
api_session.verify = False


def print_json_output(about: str, payload: dict):
    print(about)
    print(json.dumps(payload, indent=2))
    print('*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*\r\n')

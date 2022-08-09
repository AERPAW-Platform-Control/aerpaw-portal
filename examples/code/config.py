# configuration to be used by scripts found in examples/code
import requests

# User to provide appropriate values
API_URL = 'https://127.0.0.1:8443/api'
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...RfvRnEoxaAxrz93-Q8MIGggyi4EEdklSqw2OqGN2lz0'
REFRESH_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...8PSBzKFWiYqKOxBHwi7LZ6T89uH5tz0L01s0gVoqOOU'

headers = {
    'Authorization': 'Bearer ' + ACCESS_TOKEN,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

api_session = requests.Session()
api_session.headers = headers

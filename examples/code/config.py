# configuration to be used by scripts found in examples/code
import requests

# User to provide appropriate values
API_URL = 'http://aerpaw-dev.renci.org:8000/api'
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYwMTAwMjM2LCJpYXQiOjE2NjAwNTcwMzYsImp0aSI6ImNmNTIzZTk2ZGNhZjQ2MjFhYWRkNzg0MmJjYTE0ODg4IiwidXNlcl9pZCI6MX0.RfvRnEoxaAxrz93-Q8MIGggyi4EEdklSqw2OqGN2lz0'
REFRESH_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2MDY2MTgzNiwiaWF0IjoxNjYwMDU3MDM2LCJqdGkiOiI2MmIwN2EwNTEyZmE0ZmZhYjI3NTk1NzI1YjE4MzZmYiIsInVzZXJfaWQiOjF9.8PSBzKFWiYqKOxBHwi7LZ6T89uH5tz0L01s0gVoqOOU'

headers = {
    'Authorization': 'Bearer ' + ACCESS_TOKEN,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

api_session = requests.Session()
api_session.headers = headers

""" examples/code/users.py

Examples:
    - /users: paginated list with search
    - /users/{int:pk}: detail for single user
    - /users/{int:pk}/credentials: list of user credentials
    - /users/{int:pk}/tokens: user tokens
    - /token/refresh: refresh user access_token

"""
import json

from config import api_session as api, API_URL, REFRESH_TOKEN

refresh_data = {'refresh': REFRESH_TOKEN}

"""
/users

- all users as paginated list
- search for "stea" in name or email
"""
print('')
print('*** /users: paginated list with search***')

# all users
API_CALL = API_URL + '/users'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

# search for "stea" in name or email
API_CALL = API_URL + '/users?search=stea'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
/users/{int:pk}

- details for user with pk = 1
"""
print('')
print('*** /users/{int:pk}: detail for single user ***')
API_CALL = API_URL + '/users/1'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
/users/{int:pk}/credentials

- credentials for user with pk = 1
"""
# TODO: /users/{int:pk}/credentials
print('')
print('*** /users/{int:pk}/credentials: list of user credentials ***')
API_CALL = API_URL + '/users/1/credentials'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
/users/{int:pk}/tokens

- tokens for user with pk = 1
"""
print('')
print('*** /users/{int:pk}/tokens: user tokens ***')
API_CALL = API_URL + '/users/1/tokens'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
/token/refresh/

- refresh access_token for user
- endpoint requires trailing slash
"""
print('')
print('*** /token/refresh/: refresh user access_token ***')
API_CALL = API_URL + '/token/refresh/'
data = json.dumps(refresh_data)
response = api.post(API_CALL, data=data)
python_object = json.loads(response.text)
print('*** POST: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

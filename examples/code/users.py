""" examples/code/users.py

Examples:
    - /users: paginated list of users
    - /users?search=string: paginated list of users with search
    - /users/{int:pk}: retrieve single user
    - /users/{int:pk}?display_name=string: update single user display_name
    - /users/{int:pk}/credentials: list of user credentials
    - /users/{int:pk}/tokens: retrieve user tokens
    - /users/{int:pk}/tokens?refresh=true: refresh user tokens
    - /users/{int:pk}/tokens?generate=true: generate user tokens

"""
import json

from config import api_session as api, API_URL, REFRESH_TOKEN

refresh_data = {'refresh': REFRESH_TOKEN}
user_data = {'display_name': 'Michael J. Stealey, Sr.'}

"""
GET /users

- paginated list of users
"""
print('')
print('*** /users: paginated list of users ***')
API_CALL = API_URL + '/users'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /users?search=string

- paginated list of users with search
"""
print('')
print('*** /users?search=stea: paginated list of users with search ***')
API_CALL = API_URL + '/users?search=stea'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /users/{int:pk}

- retrieve details for user with pk = 1
"""
print('')
print('*** /users/{int:pk}: retrieve details for user with pk = 1 ***')
API_CALL = API_URL + '/users/1'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
PUT /users/{int:pk}?display_name=string

- update "disoplay_name" for user with pk = 1
"""
print('')
print('*** /users/{int:pk}: update "disoplay_name" for user with pk = 1 ***')
print('*** data = {0} ***'.format(json.dumps(user_data)))
API_CALL = API_URL + '/users/1'
data = json.dumps(user_data)
response = api.put(API_CALL, data=data)
python_object = json.loads(response.text)
print('*** PUT: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /users/{int:pk}/credentials

- credentials for user with pk = 1
"""
print('')
print('*** /users/{int:pk}/credentials: credentials for user with pk = 1 ***')
API_CALL = API_URL + '/users/1/credentials'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /users/{int:pk}/tokens

- retrieve tokens for user with pk = 1
"""
print('')
print('*** /users/{int:pk}/tokens: retrieve tokens for user with pk = 1 ***')
API_CALL = API_URL + '/users/1/tokens'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /users/{int:pk}/tokens?refresh=true

- refresh tokens for user with pk = 1
"""
print('')
print('*** /users/{int:pk}/tokens?refresh=true: refresh tokens for user with pk = 1 ***')
API_CALL = API_URL + '/users/1/tokens?refresh=true'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

"""
GET /users/{int:pk}/tokens?generate=true

- generate tokens for user with pk = 1
"""
print('')
print('*** /users/{int:pk}/tokens?generate=true: generate tokens for user with pk = 1 ***')
API_CALL = API_URL + '/users/1/tokens?generate=true'
response = api.get(API_CALL)
python_object = json.loads(response.text)
print('*** GET: {0} ***'.format(API_CALL))
print(json.dumps(python_object, indent=2))

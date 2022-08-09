# Example code in Python

Example code using Python [requests](https://requests.readthedocs.io/en/latest/) library.

## Running the example code

A script has been included for each API endpoint to demonstrate simple usage in Python. It may be easiest to set up a virtual environment to run each script. Example output is also included but may have redactions to not expose any potentially private information.

### Virtual environment

[Virtualenv](https://virtualenv.pypa.io/en/latest/) will be used for the included examples

### Configuration

Update the `config.py` file with appropriate values. Initial `access_token` and `refresh_token` values can be retrieved from the AERPAW Portal user profile page.

```python
# User to provide appropriate values
API_URL = 'https://127.0.0.1:8443/api'
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...RfvRnEoxaAxrz93-Q8MIGggyi4EEdklSqw2OqGN2lz0'
REFRESH_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...8PSBzKFWiYqKOxBHwi7LZ6T89uH5tz0L01s0gVoqOOU'
```

## `canonical-experiment-resource`

## `experiments`

## `p-canonical-exeriment-number`

## `projects`

Script [`projects.py`](./code/projects.py) examples:
    
- `/projects`: paginated list with search, create new project
- `/projects/{int:pk}`: detail for single project, update single project
- `/projects/{int:pk}/experiments`: list of project experiments
- `/projects/{int:pk}/membership`: list of project membership, edit project membership

Expected [example output](./output-projects.md)

## `resources`

## `sessions`

## `user-exerperiment`

## `user-project`

## `users`

Script [`users.py`](./code/users.py) examples:

- `/users`: paginated list with search
- `/users/{int:pk}`: detail for single user
- `/users/{int:pk}/credentials`: list of user credentials
- `/users/{int:pk}/tokens`: user tokens
- `/token/refresh`: refresh user access_token

Expected [example output](./output-users.md)


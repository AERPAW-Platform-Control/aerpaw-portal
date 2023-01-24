# Example code in Python

**WORK IN PROGRESS**

Example code using Python [requests](https://requests.readthedocs.io/en/latest/) library (Python 3).

It is left to the user to ensure they have current versions of **python3** and **pip3** installed on their system.

## API Endpoints

The example code herein is meant to illustrate how to interact with the AERPAW portal API endpoints in a programmatic way.

The documentation will be presented using a local deployment of the portal populated with sample data

- local deployment: [https://127.0.0.1:8443/api/]()
- sample data: snapshot taken from portal in Jan 2023

### API endpoints as of version 1.0.0

```json
{
    "canonical-experiment-resource": "https://127.0.0.1:8443/api/canonical-experiment-resource",
    "credentials": "https://127.0.0.1:8443/api/credentials",
    "experiment-files": "https://127.0.0.1:8443/api/experiment-files",
    "experiments": "https://127.0.0.1:8443/api/experiments",
    "messages": "https://127.0.0.1:8443/api/messages",
    "p-canonical-experiment-number": "https://127.0.0.1:8443/api/p-canonical-experiment-number",
    "projects": "https://127.0.0.1:8443/api/projects",
    "requests": "https://127.0.0.1:8443/api/requests",
    "resources": "https://127.0.0.1:8443/api/resources",
    "sessions": "https://127.0.0.1:8443/api/sessions",
    "user-experiment": "https://127.0.0.1:8443/api/user-experiment",
    "user-project": "https://127.0.0.1:8443/api/user-project",
    "users": "https://127.0.0.1:8443/api/users"
}
```
---

## Table of Contents

- [canonical-experiment-resource](./canonical-experiment-resource.md)
- [credentials](./credentials.md)
- [experiment-files](./experiment-files.md)
- [experiments](./experiments.md)
- [messages](./messages.md)
- [p-canonical-experiment-number](./p-canonical-experiment-number.md)
- [projects](./projects.md)
- [requests](./requests.md)
- [resources](./resources.md)
- [sessions](./sessions.md)
- [user-experiment](./user-experiment.md)
- [user-project](./user-project.md)
- [users](./users.md)

---

## How to run the example code

A script has been included for each API endpoint to demonstrate simple usage in Python. It may be easiest to set up a virtual environment to run each script. Example output is also included but may have redactions to not expose any potentially private information.

### Virtual environment

[Virtualenv](https://virtualenv.pypa.io/en/latest/) will be used for the included examples.

```
$ cd aerpaw-portal/examples/code
$ virtualenv -p /usr/local/bin/python3 venv
$ source venv/bin/activate
(venv)$ pip install -r requirements.txt
```

**NOTE**: `/usr/local/bin/python3` is the full path to Python on my local machine, yours may be different... adjust accordingly

### Configuration

Update the `config.py` file with appropriate values. Initial `access_token` and `refresh_token` values can be retrieved from the AERPAW Portal user profile page.

```python
# User to provide appropriate values
API_URL = 'https://127.0.0.1:8443/api'
ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...RfvRnEoxaAxrz93-Q8MIGggyi4EEdklSqw2OqGN2lz0'
REFRESH_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...8PSBzKFWiYqKOxBHwi7LZ6T89uH5tz0L01s0gVoqOOU'
```

### Running the code

With the virtual environment set the user should be able to run each script. It is important to verify that the example data used in each script is valid for your particular deployment.

Using `projects.py` as an example, verify that the sample data is valid

```python
...
# data below was populated knowing that Users exist for ID 1 and 3
project_data = {
    'name': 'example code project',
    'description': 'example code project description',
    'is_public': False
}
updated_project_data = {
    'description': 'updated example code project description',
    'is_public': True
}
project_membership = {
    "project_members": [1, 3],
    "project_owners": [1, 3]
}
...
```

From the terminal where you've activated the virtual environment, issue the appropriate python call: `python -m SCRIPT_NAME`

So a call to run the `projects.py` script would look like:

```console
(venv)$ python -m projects
```





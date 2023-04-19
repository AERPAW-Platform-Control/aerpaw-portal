## API `/experiments`

### Endpoints

**`/experiments`**

- GET: paginated list of experiments
- POST: create new experiment
    - data required: `description` as string
    - data required: `name` as string
    - data required: `project_id` as int

**`/experiments?search=<string>`**

- GET: paginated list of experiments where `<string>` is used as a search term against `name`

**`/experiments/{int:pk}`**

- GET: retrieve a single user by `experiment_id`
- PUT: update a single user by `experiment_id`
    - data optional: `description` as string
    - data optional: `is_public` as boolean
    - data optional: `name` as string
- DELETE: soft delete experiment by `experiment_id`

**`/experiments/{int:pk}/files`**

- GET: retrieve experiment files for experiment by `experiment_id`
- PUT: update experiment files from experiment by `experiment_id`
    - data optional: `experiment_files` as array of experiment file objects

**`/experiments/{int:pk}/membership`**

- GET: retrieve membership for experiment by `experiment_id`
- PUT: update membership from experiment by `experiment_id`
    - data optional: `experiment_members` as array of int

**`/experiments/{int:pk}/resources`**

- GET: retrieve resources for experiment by `experiment_id`
- PUT: update resources from experiment by `experiment_id`
    - data optional: `experiment_members` as array of int

**`/experiments/{int:pk}/sessions`**

- GET: retrieve resources for experiment by `experiment_id`
- PUT: update resources from experiment by `experiment_id`
    - data optional: `experiment_members` as array of int

**`/experiments/{int:pk}/state`**

- GET: retrieve resources for experiment by `experiment_id`
- PUT: update resources from experiment by `experiment_id`
    - data optional: `experiment_members` as array of int



### Example Code

From [code/experiments.py](./code/experiments.py)

```python
if __name__ == '__main__':
    get_experiments_list()
    post_experiments_create()
    get_experiments_list_search()
    get_experiments_detail()
    put_experiments_detail()
    get_experiments_detail_experiments()
    get_experiments_detail_membership()
    put_experiments_detail_membership()
    get_experiments_detail()
    delete_experiments_detail()
```

### Output from example code

Output observed from running the `experiments.py` script

```console
(venv)$ python -m experiments
*** GET: https://127.0.0.1:8443/api/experiments ***
{
  "count": 26,
  "next": "https://127.0.0.1:8443/api/experiments?page=2",
  "previous": null,
  "results": [
    {
      "created_date": "2022-03-22T11:52:45.836000-04:00",
      "description": "The end goal of the AERPAW-based evaluation is to demonstrate a proof-of-concept of an adaptive UAV-assisted wireless network that embeds functionalities such as adaptive rate and power control, user association, and trajectory adaptation based on real-time propagation conditions. The experimental activities of years 1-5 define the building blocks towards this end goal.",
      "is_public": false,
      "membership": {
        "is_experiment_creator": false,
        "is_experiment_member": false,
        "is_experiment_owner": false
      },
      "name": "Adaptive Communications and Trajectory Design for UAV-assisted Wireless Networks",
      "experiment_creator": 89,
      "experiment_id": 34
    },
    {
      "created_date": "2021-09-02T12:25:45.157000-04:00",
      "description": "This experiment will include 5 experimetns called ExEp1 ... ExEp5.",
      "is_public": false,
      "membership": {
        "is_experiment_creator": false,
        "is_experiment_member": false,
        "is_experiment_owner": false
      },
      "name": "AERPAW Alpha Testing",
      "experiment_creator": 16,
      "experiment_id": 12
    },
    ...
    {
      "created_date": "2022-06-09T15:09:44.925000-04:00",
      "description": "demo",
      "is_public": true,
      "membership": {
        "is_experiment_creator": true,
        "is_experiment_member": false,
        "is_experiment_owner": false
      },
      "name": "demo",
      "experiment_creator": 2,
      "experiment_id": 39
    },
    {
      "created_date": "2021-10-14T22:02:02.583000-04:00",
      "description": "ECE 578 group experiment with Tanisha and Hrishikesh",
      "is_public": false,
      "membership": {
        "is_experiment_creator": false,
        "is_experiment_member": false,
        "is_experiment_owner": false
      },
      "name": "Drone Communication",
      "experiment_creator": 23,
      "experiment_id": 22
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** POST: https://127.0.0.1:8443/api/experiments ***
{
  "created_date": "2023-01-25T22:09:50.431080-05:00",
  "description": "demo experiment for testing purposes",
  "is_public": true,
  "last_modified_by": 2,
  "membership": {
    "is_experiment_creator": true,
    "is_experiment_member": false,
    "is_experiment_owner": true
  },
  "modified_date": "2023-01-25T22:09:50.431091-05:00",
  "name": "demo experiment",
  "experiment_creator": 2,
  "experiment_id": 48,
  "experiment_members": [],
  "experiment_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.434252-05:00",
      "user_id": 2
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/experiments?search=demo ***
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "created_date": "2022-06-09T15:09:44.925000-04:00",
      "description": "demo",
      "is_public": true,
      "membership": {
        "is_experiment_creator": true,
        "is_experiment_member": false,
        "is_experiment_owner": false
      },
      "name": "demo",
      "experiment_creator": 2,
      "experiment_id": 39
    },
    {
      "created_date": "2023-01-25T22:09:50.431080-05:00",
      "description": "demo experiment for testing purposes",
      "is_public": true,
      "membership": {
        "is_experiment_creator": true,
        "is_experiment_member": false,
        "is_experiment_owner": true
      },
      "name": "demo experiment",
      "experiment_creator": 2,
      "experiment_id": 48
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/experiments/48 ***
{
  "created_date": "2023-01-25T22:09:50.431080-05:00",
  "description": "demo experiment for testing purposes",
  "is_public": true,
  "last_modified_by": 2,
  "membership": {
    "is_experiment_creator": true,
    "is_experiment_member": false,
    "is_experiment_owner": true
  },
  "modified_date": "2023-01-25T22:09:50.431091-05:00",
  "name": "demo experiment",
  "experiment_creator": 2,
  "experiment_id": 48,
  "experiment_members": [],
  "experiment_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.434252-05:00",
      "user_id": 2
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** PUT: https://127.0.0.1:8443/api/experiments/48 ***
{
  "created_date": "2023-01-25T22:09:50.431080-05:00",
  "description": "demo experiment for testing purposes - updated",
  "is_public": false,
  "last_modified_by": 2,
  "membership": {
    "is_experiment_creator": true,
    "is_experiment_member": false,
    "is_experiment_owner": true
  },
  "modified_date": "2023-01-25T22:09:50.557424-05:00",
  "name": "demo experiment",
  "experiment_creator": 2,
  "experiment_id": 48,
  "experiment_members": [],
  "experiment_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.434252-05:00",
      "user_id": 2
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/experiments/48/experiments ***
[]
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/experiments/48/membership ***
{
  "experiment_members": [],
  "experiment_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.434252-05:00",
      "user_id": 2
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** PUT: https://127.0.0.1:8443/api/experiments/48/membership ***
{
  "experiment_members": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.669460-05:00",
      "user_id": 12
    }
  ],
  "experiment_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.832112-05:00",
      "user_id": 11
    },
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.842457-05:00",
      "user_id": 22
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/experiments/48 ***
{
  "created_date": "2023-01-25T22:09:50.431080-05:00",
  "description": "demo experiment for testing purposes - updated",
  "is_public": false,
  "last_modified_by": 2,
  "membership": {
    "is_experiment_creator": true,
    "is_experiment_member": false,
    "is_experiment_owner": false
  },
  "modified_date": "2023-01-25T22:09:50.557424-05:00",
  "name": "demo experiment",
  "experiment_creator": 2,
  "experiment_id": 48,
  "experiment_members": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.669460-05:00",
      "user_id": 12
    }
  ],
  "experiment_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.832112-05:00",
      "user_id": 11
    },
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.842457-05:00",
      "user_id": 22
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** DELETE: https://127.0.0.1:8443/api/experiments/48 ***
- Response: <Response [204]>
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


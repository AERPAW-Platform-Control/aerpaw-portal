## API `/projects`

### Endpoints

**`/projects`**

- GET: paginated list of projects
- POST: create new project
    - data required: `description` as string
    - data required: `is_public` as boolean
    - data required: `name` as string

**`/projects?search=<string>`**

- GET: paginated list of projects where `<string>` is used as a search term against `name`

**`/projects/{int:pk}`**

- GET: retrieve a single user by `project_id`
- PUT: update a single user by `project_id`
    - data optional: `description` as string
    - data optional: `is_public` as boolean
    - data optional: `name` as string

**`/projects/{int:pk}/experiments`**

- GET: retrieve list of experiments for project by `project_id`

**`/projects/{int:pk}/membership`**

- GET: retrieve membership for project by `project_id`
- PUT: update membership from project by `project_id`
    - data optional: `project_members` as array of int
    - data optional: `project_owners` as array of int

**`/projects/{int:pk}`**

- DELETE: soft delete project by `project_id`

### Example Code

From [code/projects.py](./code/projects.py)

```python
if __name__ == '__main__':
    get_projects_list()
    post_projects_create()
    get_projects_list_search()
    get_projects_detail()
    put_projects_detail()
    get_projects_detail_experiments()
    get_projects_detail_membership()
    put_projects_detail_membership()
    get_projects_detail()
    delete_projects_detail()
```

### Output from example code

Output observed from running the `projects.py` script

```console
(venv)$ python -m projects
*** GET: https://127.0.0.1:8443/api/projects ***
{
  "count": 26,
  "next": "https://127.0.0.1:8443/api/projects?page=2",
  "previous": null,
  "results": [
    {
      "created_date": "2022-03-22T11:52:45.836000-04:00",
      "description": "The end goal of the AERPAW-based evaluation is to demonstrate a proof-of-concept of an adaptive UAV-assisted wireless network that embeds functionalities such as adaptive rate and power control, user association, and trajectory adaptation based on real-time propagation conditions. The experimental activities of years 1-5 define the building blocks towards this end goal.",
      "is_public": false,
      "membership": {
        "is_project_creator": false,
        "is_project_member": false,
        "is_project_owner": false
      },
      "name": "Adaptive Communications and Trajectory Design for UAV-assisted Wireless Networks",
      "project_creator": 89,
      "project_id": 34
    },
    {
      "created_date": "2021-09-02T12:25:45.157000-04:00",
      "description": "This project will include 5 experimetns called ExEp1 ... ExEp5.",
      "is_public": false,
      "membership": {
        "is_project_creator": false,
        "is_project_member": false,
        "is_project_owner": false
      },
      "name": "AERPAW Alpha Testing",
      "project_creator": 16,
      "project_id": 12
    },
    ...
    {
      "created_date": "2022-06-09T15:09:44.925000-04:00",
      "description": "demo",
      "is_public": true,
      "membership": {
        "is_project_creator": true,
        "is_project_member": false,
        "is_project_owner": false
      },
      "name": "demo",
      "project_creator": 2,
      "project_id": 39
    },
    {
      "created_date": "2021-10-14T22:02:02.583000-04:00",
      "description": "ECE 578 group project with Tanisha and Hrishikesh",
      "is_public": false,
      "membership": {
        "is_project_creator": false,
        "is_project_member": false,
        "is_project_owner": false
      },
      "name": "Drone Communication",
      "project_creator": 23,
      "project_id": 22
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** POST: https://127.0.0.1:8443/api/projects ***
{
  "created_date": "2023-01-25T22:09:50.431080-05:00",
  "description": "demo project for testing purposes",
  "is_public": true,
  "last_modified_by": 2,
  "membership": {
    "is_project_creator": true,
    "is_project_member": false,
    "is_project_owner": true
  },
  "modified_date": "2023-01-25T22:09:50.431091-05:00",
  "name": "demo project",
  "project_creator": 2,
  "project_id": 48,
  "project_members": [],
  "project_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.434252-05:00",
      "user_id": 2
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/projects?search=demo ***
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
        "is_project_creator": true,
        "is_project_member": false,
        "is_project_owner": false
      },
      "name": "demo",
      "project_creator": 2,
      "project_id": 39
    },
    {
      "created_date": "2023-01-25T22:09:50.431080-05:00",
      "description": "demo project for testing purposes",
      "is_public": true,
      "membership": {
        "is_project_creator": true,
        "is_project_member": false,
        "is_project_owner": true
      },
      "name": "demo project",
      "project_creator": 2,
      "project_id": 48
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/projects/48 ***
{
  "created_date": "2023-01-25T22:09:50.431080-05:00",
  "description": "demo project for testing purposes",
  "is_public": true,
  "last_modified_by": 2,
  "membership": {
    "is_project_creator": true,
    "is_project_member": false,
    "is_project_owner": true
  },
  "modified_date": "2023-01-25T22:09:50.431091-05:00",
  "name": "demo project",
  "project_creator": 2,
  "project_id": 48,
  "project_members": [],
  "project_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.434252-05:00",
      "user_id": 2
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** PUT: https://127.0.0.1:8443/api/projects/48 ***
{
  "created_date": "2023-01-25T22:09:50.431080-05:00",
  "description": "demo project for testing purposes - updated",
  "is_public": false,
  "last_modified_by": 2,
  "membership": {
    "is_project_creator": true,
    "is_project_member": false,
    "is_project_owner": true
  },
  "modified_date": "2023-01-25T22:09:50.557424-05:00",
  "name": "demo project",
  "project_creator": 2,
  "project_id": 48,
  "project_members": [],
  "project_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.434252-05:00",
      "user_id": 2
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/projects/48/experiments ***
[]
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/projects/48/membership ***
{
  "project_members": [],
  "project_owners": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.434252-05:00",
      "user_id": 2
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** PUT: https://127.0.0.1:8443/api/projects/48/membership ***
{
  "project_members": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.669460-05:00",
      "user_id": 12
    }
  ],
  "project_owners": [
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

*** GET: https://127.0.0.1:8443/api/projects/48 ***
{
  "created_date": "2023-01-25T22:09:50.431080-05:00",
  "description": "demo project for testing purposes - updated",
  "is_public": false,
  "last_modified_by": 2,
  "membership": {
    "is_project_creator": true,
    "is_project_member": false,
    "is_project_owner": false
  },
  "modified_date": "2023-01-25T22:09:50.557424-05:00",
  "name": "demo project",
  "project_creator": 2,
  "project_id": 48,
  "project_members": [
    {
      "granted_by": 2,
      "granted_date": "2023-01-25T22:09:50.669460-05:00",
      "user_id": 12
    }
  ],
  "project_owners": [
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

*** DELETE: https://127.0.0.1:8443/api/projects/48 ***
- Response: <Response [204]>
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


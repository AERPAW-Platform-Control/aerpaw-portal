Output observed from running the `projects.py` script

```console
$ python -m projects

*** /projects: paginated list with search***
*** GET: http://aerpaw-dev.renci.org:8000/api/projects ***
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "created_date": "2022-08-05T16:23:08.691073-04:00",
      "description": "Dummy project",
      "is_public": false,
      "membership": {
        "is_project_creator": false,
        "is_project_member": false,
        "is_project_owner": false
      },
      "name": "Dummy project",
      "project_creator": 2,
      "project_id": 1
    },
    {
      "created_date": "2022-08-09T15:15:00.085584-04:00",
      "description": "stealey demo project",
      "is_public": false,
      "membership": {
        "is_project_creator": true,
        "is_project_member": false,
        "is_project_owner": true
      },
      "name": "stealey demo",
      "project_creator": 1,
      "project_id": 2
    }
  ]
}
*** GET: http://aerpaw-dev.renci.org:8000/api/projects?search=stea ***
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "created_date": "2022-08-09T15:15:00.085584-04:00",
      "description": "stealey demo project",
      "is_public": false,
      "membership": {
        "is_project_creator": true,
        "is_project_member": false,
        "is_project_owner": true
      },
      "name": "stealey demo",
      "project_creator": 1,
      "project_id": 2
    }
  ]
}

*** /projects/{int:pk}: detail for single project ***
*** GET: http://aerpaw-dev.renci.org:8000/api/projects/2 ***
{
  "created_date": "2022-08-09T15:15:00.085584-04:00",
  "description": "stealey demo project",
  "is_public": false,
  "last_modified_by": 1,
  "membership": {
    "is_project_creator": true,
    "is_project_member": false,
    "is_project_owner": true
  },
  "modified_date": "2022-08-09T15:15:00.085603-04:00",
  "name": "stealey demo",
  "project_creator": 1,
  "project_id": 2,
  "project_members": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T15:15:35.953645-04:00",
      "user_id": 3
    }
  ],
  "project_owners": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T15:15:00.088392-04:00",
      "user_id": 1
    }
  ]
}

*** /projects/{int:pk}/experiments: list of project experiments ***
*** GET: http://aerpaw-dev.renci.org:8000/api/projects/2/experiments ***
[
  {
    "canonical_number": 2,
    "created_date": "2022-08-09T15:16:08.084464-04:00",
    "description": "stealey api docs example",
    "experiment_creator": 1,
    "experiment_id": 2,
    "experiment_uuid": "46710a65-97b3-4a57-83da-389a95ccceed",
    "is_canonical": true,
    "is_retired": false,
    "name": "stealey api docs"
  }
]

*** /projects/{int:pk}/membership: list of project membership, edit project membership ***
*** GET: http://aerpaw-dev.renci.org:8000/api/projects/2/membership ***
{
  "project_members": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T15:15:35.953645-04:00",
      "user_id": 3
    }
  ],
  "project_owners": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T15:15:00.088392-04:00",
      "user_id": 1
    }
  ]
}

*** /projects: create new project***
*** POST: http://aerpaw-dev.renci.org:8000/api/projects ***
{
  "created_date": "2022-08-09T15:58:11.836397-04:00",
  "description": "example code project description",
  "is_public": false,
  "last_modified_by": 1,
  "membership": {
    "is_project_creator": true,
    "is_project_member": false,
    "is_project_owner": true
  },
  "modified_date": "2022-08-09T15:58:11.836418-04:00",
  "name": "example code project",
  "project_creator": 1,
  "project_id": 3,
  "project_members": [],
  "project_owners": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T15:58:11.838893-04:00",
      "user_id": 1
    }
  ]
}

*** /projects/{int:pk}: update existing project ***
*** PUT: http://aerpaw-dev.renci.org:8000/api/projects/3 ***
{
  "created_date": "2022-08-09T15:58:11.836397-04:00",
  "description": "updated example code project description",
  "is_public": true,
  "last_modified_by": 1,
  "membership": {
    "is_project_creator": true,
    "is_project_member": false,
    "is_project_owner": true
  },
  "modified_date": "2022-08-09T15:58:11.901527-04:00",
  "name": "example code project",
  "project_creator": 1,
  "project_id": 3,
  "project_members": [],
  "project_owners": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T15:58:11.838893-04:00",
      "user_id": 1
    }
  ]
}

*** /projects/{int:pk}/membership: update project membership ***
*** PUT: http://aerpaw-dev.renci.org:8000/api/projects/3/membership ***
{
  "project_members": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T16:22:51.258286-04:00",
      "user_id": 1
    },
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T16:28:59.189515-04:00",
      "user_id": 3
    }
  ],
  "project_owners": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T15:58:11.838893-04:00",
      "user_id": 1
    },
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T16:22:51.268324-04:00",
      "user_id": 3
    }
  ]
}

*** /projects/{int:pk}: detail for single project ***
*** GET: http://aerpaw-dev.renci.org:8000/api/projects/3 ***
{
  "created_date": "2022-08-09T15:58:11.836397-04:00",
  "description": "updated example code project description",
  "is_public": true,
  "last_modified_by": 1,
  "membership": {
    "is_project_creator": true,
    "is_project_member": true,
    "is_project_owner": true
  },
  "modified_date": "2022-08-09T15:58:11.901527-04:00",
  "name": "example code project",
  "project_creator": 1,
  "project_id": 3,
  "project_members": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T16:22:51.258286-04:00",
      "user_id": 1
    },
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T16:28:59.189515-04:00",
      "user_id": 3
    }
  ],
  "project_owners": [
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T15:58:11.838893-04:00",
      "user_id": 1
    },
    {
      "granted_by": 1,
      "granted_date": "2022-08-09T16:22:51.268324-04:00",
      "user_id": 3
    }
  ]
}
```

## API `/user-project`

Many-to-many relationship between users and projects for:

- `project_member`
- `project_owner`

A `project_creator` is associated to the Project object itself, but could also be added as a `project_member` or `project_owner`

### Endpoints

**`/user-project`**

- GET: paginated list of user-project relations

**`/user-project?user_id=<int>`**

- GET: paginated list of user-project relations where `?user_id=<int>` is used to search for Users by `user_id`

**`/user-project?project_id=<int>`**

- GET: paginated list of user-project relations where `?project_id=<int>` is used to search for Projects by `project_id`

**`/user-project/{int:pk}`**

- GET: retrieve a single user by `project_id`

### Example Code

From [code/user-project.py](./code/user-project.py)

```python
if __name__ == '__main__':
    get_user_project_list()
    get_user_project_list_search()
    get_user_project_detail()
```

### Output from example code

Output observed from running the `user-project.py` script

```console
(venv)$ python -m user-project
*** GET: https://127.0.0.1:8443/api/user-project ***
{
  "count": 63,
  "next": "https://127.0.0.1:8443/api/user-project?page=2",
  "previous": null,
  "results": [
    {
      "granted_by": 88,
      "granted_date": "2022-11-09T13:21:35.824000-05:00",
      "id": 61,
      "project_id": 45,
      "project_role": "project_owner",
      "user_id": 54
    },
    {
      "granted_by": 88,
      "granted_date": "2022-11-09T13:21:35.824000-05:00",
      "id": 62,
      "project_id": 45,
      "project_role": "project_member",
      "user_id": 54
    },
    ...
    {
      "granted_by": 107,
      "granted_date": "2022-06-14T14:14:12.992000-04:00",
      "id": 57,
      "project_id": 41,
      "project_role": "project_member",
      "user_id": 108
    },
    {
      "granted_by": 102,
      "granted_date": "2022-06-10T16:16:17.033000-04:00",
      "id": 54,
      "project_id": 40,
      "project_role": "project_member",
      "user_id": 103
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/user-project?project_id=27 ***
{
  "count": 7,
  "next": null,
  "previous": null,
  "results": [
    {
      "granted_by": 45,
      "granted_date": "2021-11-22T18:19:58.188000-05:00",
      "id": 22,
      "project_id": 27,
      "project_role": "project_owner",
      "user_id": 72
    },
    {
      "granted_by": 45,
      "granted_date": "2021-11-22T18:19:58.188000-05:00",
      "id": 23,
      "project_id": 27,
      "project_role": "project_member",
      "user_id": 45
    },
    ...
    {
      "granted_by": 45,
      "granted_date": "2021-11-22T18:19:58.188000-05:00",
      "id": 27,
      "project_id": 27,
      "project_role": "project_member",
      "user_id": 109
    },
    {
      "granted_by": 45,
      "granted_date": "2021-11-22T18:19:58.188000-05:00",
      "id": 28,
      "project_id": 27,
      "project_role": "project_member",
      "user_id": 119
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/user-project/22 ***
{
  "granted_by": 45,
  "granted_date": "2021-11-22T18:19:58.188000-05:00",
  "id": 22,
  "project_id": 27,
  "project_role": "project_owner",
  "user_id": 72
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

```


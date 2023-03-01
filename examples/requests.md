## API `/requests`

### Endpoints

**`/requests`**

- GET: paginated list of requests
  - if user is `site_admin` all requests are returned
  - is user is not `site_admin` only self requests are returned

**`/requests?<param>=<value>`**

- GET: paginated list of requests where `<value>` is used to search for specific requests by `param`
  - response varies based on role and status of user relative to the request
  - `show_completed` can be used in conjunction with any of the parameters (value is `false` by default)


`<param>` | `<value>` | Accessible by
:---------|:----------|:-------
`experiment_id` | `int` | experiment creator or member
`project_id` | `int` | project creator, owner or member
`request_type` | `experiment`, `project`, `role` | user associated to request type
`role_user_id` | `int` | `site_admin` role
`show_completed` | `true`, `false` | usable by any valid call
`user_id` | `int` | `site_admin` role or as self

**`/requests/{int:pk}`**

- GET: retrieve a single requests by `request_id `
  - if user is requestor or recipient
- DELETE: removed a single requests by `request_id` (soft delete)
  - if user is owner of the request

### Example Code

From [code/requests-api.py](./code/requests-api.py) (cannot name `requests.py` as it collides with the package of the same name)

```python
if __name__ == '__main__':
    get_requests_list()
    get_requests_list_search()
    get_requests_detail()
    # delete_requests_detail()
```

### Output from example code

Output observed from running the `requests.py` script

```console
(venv)$ python -m requests-api
*** GET: https://127.0.0.1:8443/api/requests ***
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "is_approved": null,
      "received_by": [
        11
      ],
      "request_id": 17,
      "request_note": "[Rudra (NCSU)'s test public project] - project join request",
      "request_type": "project",
      "request_type_id": 29,
      "requested_by": 131,
      "requested_date": "2023-01-31T15:40:55.756549-05:00"
    },
    {
      "is_approved": null,
      "received_by": [
        1,
        22,
        11,
        6,
        2,
        8,
        100
      ],
      "request_id": 16,
      "request_note": "[pi] - role request",
      "request_type": "role",
      "request_type_id": 131,
      "requested_by": 131,
      "requested_date": "2023-01-31T15:33:52.484041-05:00"
    },
    ...
    {
      "is_approved": null,
      "received_by": [
        39
      ],
      "request_id": 4,
      "request_note": "[Akotbi] - experiment join request",
      "request_type": "experiment",
      "request_type_id": 64,
      "requested_by": 122,
      "requested_date": "2023-01-17T07:13:53.073706-05:00"
    },
    {
      "is_approved": null,
      "received_by": [
        2
      ],
      "request_id": 1,
      "request_note": "[demo] - project join request",
      "request_type": "project",
      "request_type_id": 39,
      "requested_by": 122,
      "requested_date": "2023-01-17T07:13:36.026512-05:00"
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/requests?user_id=2&show_completed=true ***
{
  "count": 11,
  "next": "https://user-web-portal.aerpaw.ncsu.edu/api/requests?page=2&show_completed=true&user_id=2",
  "previous": null,
  "results": [
    {
      "is_approved": null,
      "received_by": [
        1,
        22,
        11,
        6,
        2,
        8,
        100
      ],
      "request_id": 16,
      "request_note": "[pi] - role request",
      "request_type": "role",
      "request_type_id": 131,
      "requested_by": 131,
      "requested_date": "2023-01-31T15:33:52.484041-05:00"
    },
    {
      "is_approved": false,
      "received_by": [
        1,
        22,
        11,
        6,
        2,
        8,
        100
      ],
      "request_id": 15,
      "request_note": "[pi] - role request",
      "request_type": "role",
      "request_type_id": 131,
      "requested_by": 131,
      "requested_date": "2023-01-31T15:29:46.503995-05:00"
    },
    ...
    {
      "is_approved": false,
      "received_by": [
        1,
        22,
        11,
        6,
        2,
        8,
        100,
        12
      ],
      "request_id": 7,
      "request_note": "[experimenter] - role request",
      "request_type": "role",
      "request_type_id": 131,
      "requested_by": 131,
      "requested_date": "2023-01-17T13:03:51.282527-05:00"
    },
    {
      "is_approved": true,
      "received_by": [
        1,
        22,
        11,
        6,
        2,
        8,
        100,
        12
      ],
      "request_id": 6,
      "request_note": "[experimenter] - role request",
      "request_type": "role",
      "request_type_id": 131,
      "requested_by": 131,
      "requested_date": "2023-01-17T12:45:19.976752-05:00"
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/requests/16 ***
{
  "completed_by": null,
  "completed_date": null,
  "is_approved": null,
  "last_modified_by": 131,
  "modified_date": "2023-01-31T15:33:52.490431-05:00",
  "received_by": [
    1,
    22,
    11,
    6,
    2,
    8,
    100
  ],
  "request_id": 16,
  "request_note": "[pi] - role request",
  "request_type": "role",
  "request_type_id": 131,
  "requested_by": 131,
  "requested_date": "2023-01-31T15:33:52.484041-05:00",
  "response_date": null,
  "response_note": null
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


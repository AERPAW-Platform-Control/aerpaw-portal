## API `/resources`

Two endpoints are stubbed, but not yet finished (unsure if they are needed?)

- `/resources/{int:pk}/experiments`
- `/resources/{int:pk}/projects`

### Endpoints

**`/resources`**

- GET: paginated list of resources
- POST: create new resource
    - data required: `description` as string
    - data optional: `hostname` as string
    - data optional: `ip_address` as string
    - data optional: `is_active` as boolean
    - data optional: `location` as string
    - data required: `name` as string
    - data optional: `ops_notes` as string
    - data required: `resource_class` as string in [`"allow_canonical"`, `"exclude_canonical"`]
    - data required: `resource_mode` as string in [`"sandbox"`, `"testbed"`]
    - data required: `resource_type` as string in [`"afrn"`, `"aprn"`, `"uav"`, `"ugv"`, `"3pbbe"`, `"other"`]

**`/resources?search=<string>`**

- GET: paginated list of resources where `<string>` is used as a search term against `name` and `resource_type`

**`/resources/{int:pk}`**

- GET: retrieve a single user by `resource_id`
- PUT: update a single user by `resource_id`
    - data optional: `description` as string
    - data optional: `hostname` as string
    - data optional: `ip_address` as string
    - data optional: `is_active` as boolean
    - data optional: `location` as string
    - data optional: `name` as string
    - data optional: `ops_notes` as string
    - data optional: `resource_class` as string in [`"allow_canonical"`, `"exclude_canonical"`]
    - data optional: `resource_mode` as string in [`"sandbox"`, `"testbed"`]
    - data optional: `resource_type` as string in [`"afrn"`, `"aprn"`, `"uav"`, `"ugv"`, `"3pbbe"`, `"other"`]

**`/resources/{int:pk}/experiments`**

- **TODO** GET: retrieve list of experiments targeting resource by `resource_id`

**`/resources/{int:pk}/projects`**

- **TODO** GET: retrieve list of projects targeting resource by `resource_id`

**`/resources/{int:pk}`**

- DELETE: soft delete resource by `resource_id`

### Example Code

From [code/resources.py](./code/resources.py)

```python
if __name__ == '__main__':
    get_resources_list()
    post_resources_create()
    get_resources_list_search()
    get_resources_detail()
    put_resources_detail()
    get_resources_detail_experiments()
    get_resources_detail_projects()
    delete_resources_detail()
```

### Output from example code

Output observed from running the `resources.py` script

```console
(venv)$ python -m resources
*** GET: https://127.0.0.1:8443/api/resources ***
{
  "count": 26,
  "next": "https://127.0.0.1:8443/api/resources?page=2",
  "previous": null,
  "results": [
    {
      "description": "Centennial Campus AERPAW Fixed Node 1",
      "is_active": true,
      "location": "Ground level - Main Campus Drive and Varsity Drive intersection",
      "name": "CC1",
      "resource_class": "allow_canonical",
      "resource_id": 2,
      "resource_mode": "testbed",
      "resource_type": "AFRN"
    },
    {
      "description": "Centennial Campus AERPAW Fixed Node 2",
      "is_active": true,
      "location": "Rooftop of EB2 - West End",
      "name": "CC2",
      "resource_class": "allow_canonical",
      "resource_id": 3,
      "resource_mode": "testbed",
      "resource_type": "AFRN"
    },
    ...
    {
      "description": "Large AERPAW Portable Node 1",
      "is_active": true,
      "location": "At LW1 at start of run (for mobility, needs Rover, or Large Multicopter)",
      "name": "LPN1",
      "resource_class": "allow_canonical",
      "resource_id": 4,
      "resource_mode": "testbed",
      "resource_type": "APRN"
    },
    {
      "description": "Large AERPAW Portable Node 2",
      "is_active": true,
      "location": "At LW1 at start of run (for mobility, needs Rover, or Large Multicopter)",
      "name": "LPN2",
      "resource_class": "allow_canonical",
      "resource_id": 8,
      "resource_mode": "testbed",
      "resource_type": "APRN"
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** POST: https://127.0.0.1:8443/api/resources ***
{
  "created_date": "2023-01-25T16:17:52.757490-05:00",
  "description": "demo resource for testing purposes",
  "hostname": "demo.resource.org",
  "ip_address": "213.213.213.213",
  "is_active": true,
  "last_modified_by": 2,
  "location": "in the demo area",
  "modified_date": "2023-01-25T16:17:52.757506-05:00",
  "name": "demo resource",
  "ops_notes": "this resource should be good to go",
  "resource_class": "allow_canonical",
  "resource_creator": 2,
  "resource_id": 33,
  "resource_mode": "testbed",
  "resource_type": "afrn"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/resources?search=afrn ***
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "description": "Centennial Campus AERPAW Fixed Node 1",
      "is_active": true,
      "location": "Ground level - Main Campus Drive and Varsity Drive intersection",
      "name": "CC1",
      "resource_class": "allow_canonical",
      "resource_id": 2,
      "resource_mode": "testbed",
      "resource_type": "AFRN"
    },
    {
      "description": "Centennial Campus AERPAW Fixed Node 2",
      "is_active": true,
      "location": "Rooftop of EB2 - West End",
      "name": "CC2",
      "resource_class": "allow_canonical",
      "resource_id": 3,
      "resource_mode": "testbed",
      "resource_type": "AFRN"
    },
    {
      "description": "Centennial Campus AERPAW Fixed Node 3",
      "is_active": true,
      "location": "Rooftop of Partners-1",
      "name": "CC3",
      "resource_class": "allow_canonical",
      "resource_id": 9,
      "resource_mode": "testbed",
      "resource_type": "AFRN"
    },
    {
      "description": "demo resource for testing purposes",
      "is_active": true,
      "location": "in the demo area",
      "name": "demo resource",
      "resource_class": "allow_canonical",
      "resource_id": 33,
      "resource_mode": "testbed",
      "resource_type": "afrn"
    },
    ...
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/resources/33 ***
{
  "created_date": "2023-01-25T16:17:52.757490-05:00",
  "description": "demo resource for testing purposes",
  "hostname": "demo.resource.org",
  "ip_address": "213.213.213.213",
  "is_active": true,
  "last_modified_by": 2,
  "location": "in the demo area",
  "modified_date": "2023-01-25T16:17:52.757506-05:00",
  "name": "demo resource",
  "ops_notes": "this resource should be good to go",
  "resource_class": "allow_canonical",
  "resource_creator": 2,
  "resource_id": 33,
  "resource_mode": "testbed",
  "resource_type": "afrn"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** PUT: https://127.0.0.1:8443/api/resources/33 ***
{
  "created_date": "2023-01-25T16:17:52.757490-05:00",
  "description": "demo resource for testing purposes",
  "hostname": "demo.resource.org",
  "ip_address": "213.213.213.213",
  "is_active": true,
  "last_modified_by": 2,
  "location": "in the demo area",
  "modified_date": "2023-01-25T16:17:52.852272-05:00",
  "name": "demo resource",
  "ops_notes": "update IP Address to be 123.123.123.123 on 12/12/2023",
  "resource_class": "allow_canonical",
  "resource_creator": 2,
  "resource_id": 33,
  "resource_mode": "testbed",
  "resource_type": "afrn"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** TODO: GET: https://127.0.0.1:8443/api/resources/2/experiments ***
{}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** TODO: GET: https://127.0.0.1:8443/api/resources/2/projects ***
{}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** DELETE: https://127.0.0.1:8443/api/resources/33 ***
- Response: <Response [204]>
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


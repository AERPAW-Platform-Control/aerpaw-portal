## API `/experiment-files`

### Endpoints

**`/experiment-files`**

- GET: paginated list of experiment files
  - `?search=<string>`: text search for `<string>` in name, notes or file type
- POST: create new experiment file
  - data required: `file_location` as `string`
  - data required: `file_name` as `string`
  - data optional: `file_notes` as `string`
  - data required: `file_type` as `string` in [`ip_list`, `ovpn`]

**`/experiment-files?search=<string>`**

- GET: paginated list of experiment-files where `<string>` is used to search for experiment files by name or type

**`/experiment-files/{int:pk}`**

- GET: retrieve a single experiment file by `file_id`
- PUT: update and existing experiment file by `file_id`
  - data optional: `file_location` as `string`
  - data optional: `file_name` as `string`
  - data optional: `file_notes` as `string`
  - data optional: `file_type` as `string` in [`ip_list`, `ovpn`]
  - data optional: `is_active` as `boolean`
- DELETE: soft delete experiment file by `file_id`


### Example Code

From [code/experiment-files.py](./code/experiment-files.py)

```python
if __name__ == '__main__':
    get_experiment_files_list()
    post_experiment_files_create()
    get_experiment_files_list_search()
    get_experiment_files_detail()
    put_experiment_files_detail()
    delete_experiment_files_detail()
```

### Output from example code

Output observed from running the `experiment-files.py` script

```console
(venv)$ python -m experiment-files
*** GET: https://127.0.0.1:8443/api/experiment-files ***
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "file_id": 1,
      "file_location": "/home/aerpawops/experiments/deb28110-cce3-4e02-bfc9-6e477ef8f8ec/aerpaw-XM-X0004-common.ovpn",
      "file_name": "aerpaw-XM-X0004-common.ovpn",
      "file_notes": "common OVPN file",
      "file_type": "ovpn",
      "is_active": true,
      "is_deleted": false
    },
    {
      "file_id": 2,
      "file_location": "/home/aerpawops/experiments/deb28110-cce3-4e02-bfc9-6e477ef8f8ec/Manifest.txt",
      "file_name": "Manifest-XM-X0004.txt",
      "file_notes": "IP List",
      "file_type": "ip_list",
      "is_active": true,
      "is_deleted": false
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** POST: https://127.0.0.1:8443/api/experiment-files ***
{
  "created_by": 2,
  "created_date": "2023-04-19T14:11:43.747045-04:00",
  "file_id": 3,
  "file_location": "/home/aerpawops/some/place/to/store/files",
  "file_name": "manifest-example.txt",
  "file_notes": "example manifest file for demo purposes",
  "file_type": "ip_list",
  "is_active": false,
  "is_deleted": false,
  "last_modified_by": 2,
  "modified_date": "2023-04-19T14:11:43.747067-04:00"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/experiment-files?search=example ***
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "file_id": 3,
      "file_location": "/home/aerpawops/some/place/to/store/files",
      "file_name": "manifest-example.txt",
      "file_notes": "example manifest file for demo purposes",
      "file_type": "ip_list",
      "is_active": false,
      "is_deleted": false
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/experiment-files/3 ***
{
  "created_by": 2,
  "created_date": "2023-04-19T14:11:43.747045-04:00",
  "file_id": 3,
  "file_location": "/home/aerpawops/some/place/to/store/files",
  "file_name": "manifest-example.txt",
  "file_notes": "example manifest file for demo purposes",
  "file_type": "ip_list",
  "is_active": false,
  "is_deleted": false,
  "last_modified_by": 2,
  "modified_date": "2023-04-19T14:11:43.747067-04:00"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** PUT: https://127.0.0.1:8443/api/experiment-files/3 ***
{
  "created_by": 2,
  "created_date": "2023-04-19T14:11:43.747045-04:00",
  "file_id": 3,
  "file_location": "/home/aerpawops/some/place/to/store/files",
  "file_name": "manifest-example-v2.txt",
  "file_notes": "updated example manifest file for demo purposes",
  "file_type": "ip_list",
  "is_active": false,
  "is_deleted": false,
  "last_modified_by": 2,
  "modified_date": "2023-04-19T14:11:43.885753-04:00"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** DELETE: https://127.0.0.1:8443/api/experiment-files/3 ***
- Response: <Response [204]>
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


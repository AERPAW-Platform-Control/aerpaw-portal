## API `/canonical-experiment-resource`

### Endpoints

**`/canonical-experiment-resource`**

- GET: paginated list of canonical-experiment-resource relations
  - if user is `operator` all canonical-experiment-resource relations are returned
  - is user is not `operator` only self canonical-experiment-resource relations are returned

**`/canonical-experiment-resource?experiment_id=<int>`**

- GET: paginated list of canonical-experiment-resource relations where `<int>` is used to search for a specific Experiment by `experiment_id`
  - if user is `operator` all matching canonical-experiment-resource relations are returned
  - is user is not `operator` only self matching canonical-experiment-resource relations are returned

**`/canonical-experiment-resource?resource_id=<int>`**

- GET: paginated list of canonical-experiment-resource relations where `<int>` is used to search for a specific Resource by `resource_id`
  - if user is `operator` all matching canonical-experiment-resource relations are returned
  - is user is not `operator` only self matching canonical-experiment-resource relations are returned

**`/canonical-experiment-resource/{int:pk}`**

- GET: retrieve a single canonical-experiment-resource relation by `public_key_id`
  - if user is `operator` all matching canonical-experiment-resource relations are returned
  - is user is not `operator` only self matching canonical-experiment-resource relations are returned

### Example Code

From [code/canonical-experiment-resource.py](./code/canonical-experiment-resource.py)

```python
if __name__ == '__main__':
    get_canonical_experiment_resource_list()
    get_canonical_experiment_resource_list_search()
    get_canonical_experiment_resource_detail()
```

### Output from example code

Output observed from running the `canonical-experiment-resource.py` script

```console
(venv)$ python -m canonical-experiment-resource
*** GET: https://127.0.0.1:8443/api/canonical-experiment-resource ***
{
  "count": 99,
  "next": "https://127.0.0.1:8443/api/canonical-experiment-resource?page=2",
  "previous": null,
  "results": [
    {
      "canonical_experiment_resource_id": 1,
      "experiment_id": 11,
      "experiment_node_number": 1,
      "node_display_name": "portablenode1",
      "node_type": "aprn",
      "node_uhd": "1.4.0",
      "node_vehicle": "vehicle_uav",
      "resource_id": null
    },
    {
      "canonical_experiment_resource_id": 3,
      "experiment_id": 12,
      "experiment_node_number": 1,
      "node_display_name": "portablenode1",
      "node_type": "aprn",
      "node_uhd": "1.4.0",
      "node_vehicle": "vehicle_uav",
      "resource_id": null
    },
    ...
    {
      "canonical_experiment_resource_id": 19,
      "experiment_id": 32,
      "experiment_node_number": 1,
      "node_display_name": "portablenode1",
      "node_type": "aprn",
      "node_uhd": "1.4.0",
      "node_vehicle": "vehicle_uav",
      "resource_id": null
    },
    {
      "canonical_experiment_resource_id": 21,
      "experiment_id": 35,
      "experiment_node_number": 1,
      "node_display_name": "portablenode1",
      "node_type": "aprn",
      "node_uhd": "1.4.0",
      "node_vehicle": "vehicle_uav",
      "resource_id": null
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/canonical-experiment-resource?resource_id=5 ***
{
  "count": 31,
  "next": "https://127.0.0.1:8443/api/canonical-experiment-resource?page=2&resource_id=5",
  "previous": null,
  "results": [
    {
      "canonical_experiment_resource_id": 35,
      "experiment_id": 70,
      "experiment_node_number": 1,
      "node_display_name": "'fixednode1",
      "node_type": "afrn",
      "node_uhd": "1.4.0",
      "node_vehicle": "vehicle_none",
      "resource_id": 5
    },
    {
      "canonical_experiment_resource_id": 75,
      "experiment_id": 96,
      "experiment_node_number": 1,
      "node_display_name": "'fixednode1'",
      "node_type": "afrn",
      "node_uhd": "1.4.0",
      "node_vehicle": "vehicle_none",
      "resource_id": 5
    },
    ...
    {
      "canonical_experiment_resource_id": 15,
      "experiment_id": 30,
      "experiment_node_number": 2,
      "node_display_name": "'fixednode1",
      "node_type": "afrn",
      "node_uhd": "1.4.0",
      "node_vehicle": "vehicle_none",
      "resource_id": 5
    },
    {
      "canonical_experiment_resource_id": 22,
      "experiment_id": 35,
      "experiment_node_number": 2,
      "node_display_name": "'fixednode1",
      "node_type": "afrn",
      "node_uhd": "1.4.0",
      "node_vehicle": "vehicle_none",
      "resource_id": 5
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/canonical-experiment-resource/35 ***
{
  "canonical_experiment_resource_id": 35,
  "experiment_id": 70,
  "experiment_node_number": 1,
  "node_display_name": "'fixednode1",
  "node_type": "afrn",
  "node_uhd": "1.4.0",
  "node_vehicle": "vehicle_none",
  "resource_id": 5
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


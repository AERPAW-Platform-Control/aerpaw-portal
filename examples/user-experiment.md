## API `/user-experiment`

Many-to-many relationship between users and experiments for:

- `experiment_member`

An `experiment_creator` is associated to the experiment object itself, but could also be added as a `experiment_member`

### Endpoints

**`/user-experiment`**

- GET: paginated list of user-experiment relations

**`/user-experiment?user_id=<int>`**

- GET: paginated list of user-experiment relations where `?user_id=<int>` is used to search for Users by `user_id`

**`/user-experiment?experiment_id=<int>`**

- GET: paginated list of user-experiment relations where `?experiment_id=<int>` is used to search for experiments by `experiment_id`

**`/user-experiment/{int:pk}`**

- GET: retrieve a single user by `experiment_id`

### Example Code

From [code/user-experiment.py](./code/user-experiment.py)

```python
if __name__ == '__main__':
    get_user_experiment_list()
    get_user_experiment_list_search()
    get_user_experiment_detail()
```

### Output from example code

Output observed from running the `user-experiment.py` script

```console
(venv)$ python -m user-experiment
*** GET: https://127.0.0.1:8443/api/user-experiment ***
{
  "count": 55,
  "next": "https://127.0.0.1:8443/api/user-experiment?page=2",
  "previous": null,
  "results": [
    {
      "experiment_id": 107,
      "granted_by": 119,
      "granted_date": "2022-11-18T14:22:26.982000-05:00",
      "id": 117,
      "user_id": 109
    },
    {
      "experiment_id": 107,
      "granted_by": 119,
      "granted_date": "2022-11-18T14:22:26.982000-05:00",
      "id": 118,
      "user_id": 119
    },
    ...
    {
      "experiment_id": 100,
      "granted_by": 32,
      "granted_date": "2022-09-02T15:47:00.958000-04:00",
      "id": 110,
      "user_id": 32
    },
    {
      "experiment_id": 99,
      "granted_by": 80,
      "granted_date": "2022-08-17T09:45:14.784000-04:00",
      "id": 109,
      "user_id": 80
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/user-experiment?experiment_id=107 ***
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "experiment_id": 107,
      "granted_by": 119,
      "granted_date": "2022-11-18T14:22:26.982000-05:00",
      "id": 117,
      "user_id": 109
    },
    {
      "experiment_id": 107,
      "granted_by": 119,
      "granted_date": "2022-11-18T14:22:26.982000-05:00",
      "id": 118,
      "user_id": 119
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/user-experiment/117 ***
{
  "experiment_id": 107,
  "granted_by": 119,
  "granted_date": "2022-11-18T14:22:26.982000-05:00",
  "id": 117,
  "user_id": 109
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


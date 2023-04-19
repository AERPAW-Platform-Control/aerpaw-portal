## API `/p-canonical-experiment-number`

The canonical experiment number is preserved using a file at: `aerpaw-portal/portal/apps/operations/current-canonical-number.json`

Since the value for canonical experiment number is globally unique it needs to tolerate container changes such and rebuilds or restarts.

Example file contents for `current-canonical-number.json`:

```json
{
    "current_canonical_number": 20,
    "timestamp": 1681832126
}
```

**NOTE**: the `current-canonical-number.json` file must be able to be written to by the user runnign the portal process. Adjust file permissions accordingly.

### Endpoints

**`/p-canonical-experiment-number`**

- GET: paginated list of canonical experiment numbers ordered by most recent first
  - auth: `operator` only

**`/p-canonical-experiment-number/{int:pk}`**

- GET: details for single canonical experiment number by `canonical_number_id`
  - auth: `operator` only

**`/p-canonical-experiment-number/current`**

- GET: current canonical experiment number
  - auth: `experimenter` and above

**`/p_canonical_experiment_number/current?number=int`**

- PUT: put new value for current canonical experiment number
  - param: `number` - integer from 1 to 9999
    - If the chosen number already exists the system will iteratively increase by 1 until an unused number is found
    - numbers exceeding 9999 will automatically rollover to 1
  - auth: `site_admin` only

### Example Code

From [code/p-canonical-experiment-number.py](./code/p-canonical-experiment-number.py)

```python
if __name__ == '__main__':
    get_p_canonical_experiment_number_list()
    get_p_canonical_experiment_number_detail()
    get_p_canonical_experiment_number_current()
    put_p_canonical_experiment_number_current()
```

### Output from example code

Output observed from running the `p-canonical-experiment-number.py` script

```console
(venv)$ python -m p-canonical-experiment-number
*** GET: https://127.0.0.1:8443/api/p-canonical-experiment-number ***
{
  "count": 44,
  "next": "https://127.0.0.1:8443/api/p-canonical-experiment-number?page=2",
  "previous": null,
  "results": [
    {
      "canonical_number": 107,
      "canonical_number_id": 44,
      "timestamp": "1668799347"
    },
    {
      "canonical_number": 106,
      "canonical_number_id": 43,
      "timestamp": "1668436089"
    },
    ...
    {
      "canonical_number": 99,
      "canonical_number_id": 36,
      "timestamp": "1660743915"
    },
    {
      "canonical_number": 98,
      "canonical_number_id": 35,
      "timestamp": "1656359227"
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/p-canonical-experiment-number/44 ***
{
  "canonical_number": 107,
  "canonical_number_id": 44,
  "created_date": "2022-11-18T14:22:26.982000-05:00",
  "is_deleted": false,
  "is_retired": false,
  "modified_date": "2022-11-18T14:23:21.756000-05:00",
  "timestamp": 1668799347
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/p-canonical-experiment-number/current ***
{
  "current_canonical_number": 20
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/p-canonical-experiment-number/current?number=123 ***
{
  "current_canonical_number": 123
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


## API `/sessions`

### Endpoints

**`/sessions`**

- GET: paginated list of sessions
  - if user is `operator` all sessions are returned
  - is user is not `operator` only self sessions are returned

**`/sessions?experiment_id=<int>`**

- GET: paginated list of sessions where `<int>` is used to search for a specific Experiment by `experiment_id`
  - if user is `operator` all matching sessions are returned
  - is user is not `operator` only self matching sessions are returned

**`/sessions/{int:pk}`**

- GET: retrieve a single sessions by `session_id`
  - if user is `operator` all matching sessions are returned
  - is user is not `operator` only self matching sessions are returned

### Example Code

From [code/sessions.py](./code/sessions.py)

```python
if __name__ == '__main__':
    get_sessions_list()
    get_sessions_list_search()
    get_sessions_detail()
```

### Output from example code

Output observed from running the `sessions.py` script

```console
(venv)$ python -m sessions
*** GET: https://127.0.0.1:8443/api/sessions ***
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "end_date_time": "2022-11-28T08:43:49.268000-05:00",
      "ended_by": 54,
      "experiment_id": 106,
      "is_active": false,
      "session_id": 22,
      "session_type": "development",
      "start_date_time": "2022-11-28T08:23:49.268000-05:00",
      "started_by": 54
    },
    {
      "end_date_time": "2022-10-12T10:46:56.501000-04:00",
      "ended_by": 116,
      "experiment_id": 101,
      "is_active": false,
      "session_id": 20,
      "session_type": "development",
      "start_date_time": "2022-10-12T10:26:36.501000-04:00",
      "started_by": 116
    },
    ...
    {
      "end_date_time": "2022-07-04T14:19:22.666000-04:00",
      "ended_by": 80,
      "experiment_id": 82,
      "is_active": false,
      "session_id": 25,
      "session_type": "development",
      "start_date_time": "2022-07-04T13:59:22.666000-04:00",
      "started_by": 80
    },
    {
      "end_date_time": "2022-07-04T14:29:13.247000-04:00",
      "ended_by": 30,
      "experiment_id": 70,
      "is_active": false,
      "session_id": 24,
      "session_type": "development",
      "start_date_time": "2022-07-04T14:09:13.247000-04:00",
      "started_by": 30
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/sessions?experiment_id=100 ***
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "end_date_time": "2022-09-16T10:15:56.143000-04:00",
      "ended_by": 32,
      "experiment_id": 100,
      "is_active": false,
      "session_id": 23,
      "session_type": "development",
      "start_date_time": "2022-09-16T09:55:56.143000-04:00",
      "started_by": 32
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/sessions/23 ***
{
  "created_by": 32,
  "created_time": "2022-09-02T15:47:00.958000-04:00",
  "end_date_time": "2022-09-16T10:15:56.143000-04:00",
  "ended_by": 32,
  "experiment_id": 100,
  "is_active": false,
  "modified_by": 32,
  "modified_time": "2022-09-16T10:05:56.143000-04:00",
  "session_id": 23,
  "session_type": "development",
  "start_date_time": "2022-09-16T09:55:56.143000-04:00",
  "started_by": 32
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


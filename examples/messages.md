## API `/messages`

### Endpoints

**`/messages`**

- GET: paginated list of messages
  - if user is `site_admin` all messages are returned
  - is user is not `site_admin` only self messages are returned

**`/messages?user_id=<int>`**

- GET: paginated list of messages where `<int>` is used to search for a specific Experiment by `user_id`
  - if user is `site_admin` all matching messages are returned
  - is user is not `site_admin` only self matching messages are returned

**`/messages/{int:pk}`**

- GET: retrieve a single messages by `message_id `
  - if user is sender or recipient
- DELETE: removed a single messages by `message_id` (soft delete)
  - if user is owner of the message

### Example Code

From [code/messages.py](./code/messages.py)

```python
if __name__ == '__main__':
    get_messages_list()
    get_messages_list_search()
    get_messages_detail()
    delete_messages_detail()
```

### Output from example code

Output observed from running the `messages.py` script

```console
(venv)$ python -m messages
*** GET: https://127.0.0.1:8443/api/messages ***
{
  "count": 21,
  "next": "https://user-web-portal.aerpaw.ncsu.edu/api/messages?page=2",
  "previous": null,
  "results": [
    {
      "is_deleted": false,
      "is_read": false,
      "message_body": "\nrequest_type: role\n\nrequested_by: Kwon HyeokJun\n\nrequest_note: [experimenter] - role request\nrequested_date: 01/31/2023, 15:28:32\n\nreceived_by: ['AERPAW Admin', 'Dr Rudra Dutta (rdutta@ncsu.edu)', 'Ismail Guvenc (iguvenc@ncsu.edu)', 'Kwon HyeokJun', 'Michael J. Stealey', 'Mihai (NCSU)', 'Sudhanva Nagaragadde (snagara9@ncsu.edu)']\n\ncompleted_by: Dr Magreth Jubilate Mushi (mjmushi@ncsu.edu)\nis_approved: True\nresponse_note: -----\nresponse_date: 01/31/2023, 15:39:57\n",
      "message_id": 212,
      "message_subject": "RESPONSE: [experimenter] - role request",
      "sent_by": 22,
      "sent_date": "2023-01-31T15:39:57.447469-05:00"
    },
    {
      "is_deleted": false,
      "is_read": false,
      "message_body": "\nrequest_type: role\n\nrequested_by: Kwon HyeokJun\n\nrequest_note: [pi] - role request\nrequested_date: 01/31/2023, 15:33:52\n\nreceived_by: ['AERPAW Admin', 'Dr Magreth Jubilate Mushi (mjmushi@ncsu.edu)', 'Dr Rudra Dutta (rdutta@ncsu.edu)', 'Ismail Guvenc (iguvenc@ncsu.edu)', 'Michael J. Stealey', 'Mihai (NCSU)', 'Sudhanva Nagaragadde (snagara9@ncsu.edu)']\n\ncompleted_by: -----\nis_approved: -----\nresponse_note: -----\nresponse_date: -----\n",
      "message_id": 204,
      "message_subject": "REQUEST: [pi] - role request",
      "sent_by": 131,
      "sent_date": "2023-01-31T15:33:52.532422-05:00"
    },
    ...
    {
      "is_deleted": false,
      "is_read": false,
      "message_body": "\nrequest_type: role\n\nrequested_by: Magreth Mushi (magreth.jubilate@gmail.com)\n\nrequest_note: [pi] - role request\nrequested_date: 01/30/2023, 09:58:27\n\nreceived_by: ['AERPAW Admin', 'Dr Magreth Jubilate Mushi (mjmushi@ncsu.edu)', 'Dr Rudra Dutta (rdutta@ncsu.edu)', 'Ismail Guvenc (iguvenc@ncsu.edu)', 'Michael J. Stealey', 'Mihai (NCSU)', 'Sudhanva Nagaragadde (snagara9@ncsu.edu)']\n\ncompleted_by: -----\nis_approved: -----\nresponse_note: -----\nresponse_date: -----\n",
      "message_id": 140,
      "message_subject": "REQUEST: [pi] - role request",
      "sent_by": 91,
      "sent_date": "2023-01-30T09:58:27.588553-05:00"
    },
    {
      "is_deleted": false,
      "is_read": false,
      "message_body": "\nrequest_type: role\n\nrequested_by: Magreth Mushi (magreth.jubilate@gmail.com)\n\nrequest_note: [experimenter] - role request\nrequested_date: 01/30/2023, 09:35:33\n\nreceived_by: ['AERPAW Admin', 'Dr Rudra Dutta (rdutta@ncsu.edu)', 'Ismail Guvenc (iguvenc@ncsu.edu)', 'Magreth Mushi (magreth.jubilate@gmail.com)', 'Michael J. Stealey', 'Mihai (NCSU)', 'Sudhanva Nagaragadde (snagara9@ncsu.edu)']\n\ncompleted_by: Dr Magreth Jubilate Mushi (mjmushi@ncsu.edu)\nis_approved: True\nresponse_note: Your request is approved. Welcome to AERPAW\nresponse_date: 01/30/2023, 09:45:36\n",
      "message_id": 132,
      "message_subject": "RESPONSE: [experimenter] - role request",
      "sent_by": 22,
      "sent_date": "2023-01-30T09:45:36.448022-05:00"
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/messages?user_id=2 ***
{
  "count": 21,
  "next": "https://user-web-portal.aerpaw.ncsu.edu/api/messages?page=2&user_id=2",
  "previous": null,
  "results": [
    {
      "is_deleted": false,
      "is_read": false,
      "message_body": "\nrequest_type: role\n\nrequested_by: Kwon HyeokJun\n\nrequest_note: [experimenter] - role request\nrequested_date: 01/31/2023, 15:28:32\n\nreceived_by: ['AERPAW Admin', 'Dr Rudra Dutta (rdutta@ncsu.edu)', 'Ismail Guvenc (iguvenc@ncsu.edu)', 'Kwon HyeokJun', 'Michael J. Stealey', 'Mihai (NCSU)', 'Sudhanva Nagaragadde (snagara9@ncsu.edu)']\n\ncompleted_by: Dr Magreth Jubilate Mushi (mjmushi@ncsu.edu)\nis_approved: True\nresponse_note: -----\nresponse_date: 01/31/2023, 15:39:57\n",
      "message_id": 212,
      "message_subject": "RESPONSE: [experimenter] - role request",
      "sent_by": 22,
      "sent_date": "2023-01-31T15:39:57.447469-05:00"
    },
    {
      "is_deleted": false,
      "is_read": false,
      "message_body": "\nrequest_type: role\n\nrequested_by: Kwon HyeokJun\n\nrequest_note: [pi] - role request\nrequested_date: 01/31/2023, 15:33:52\n\nreceived_by: ['AERPAW Admin', 'Dr Magreth Jubilate Mushi (mjmushi@ncsu.edu)', 'Dr Rudra Dutta (rdutta@ncsu.edu)', 'Ismail Guvenc (iguvenc@ncsu.edu)', 'Michael J. Stealey', 'Mihai (NCSU)', 'Sudhanva Nagaragadde (snagara9@ncsu.edu)']\n\ncompleted_by: -----\nis_approved: -----\nresponse_note: -----\nresponse_date: -----\n",
      "message_id": 204,
      "message_subject": "REQUEST: [pi] - role request",
      "sent_by": 131,
      "sent_date": "2023-01-31T15:33:52.532422-05:00"
    },
    ...
    {
      "is_deleted": false,
      "is_read": false,
      "message_body": "\nrequest_type: role\n\nrequested_by: Magreth Mushi (magreth.jubilate@gmail.com)\n\nrequest_note: [pi] - role request\nrequested_date: 01/30/2023, 09:58:27\n\nreceived_by: ['AERPAW Admin', 'Dr Magreth Jubilate Mushi (mjmushi@ncsu.edu)', 'Dr Rudra Dutta (rdutta@ncsu.edu)', 'Ismail Guvenc (iguvenc@ncsu.edu)', 'Michael J. Stealey', 'Mihai (NCSU)', 'Sudhanva Nagaragadde (snagara9@ncsu.edu)']\n\ncompleted_by: -----\nis_approved: -----\nresponse_note: -----\nresponse_date: -----\n",
      "message_id": 140,
      "message_subject": "REQUEST: [pi] - role request",
      "sent_by": 91,
      "sent_date": "2023-01-30T09:58:27.588553-05:00"
    },
    {
      "is_deleted": false,
      "is_read": false,
      "message_body": "\nrequest_type: role\n\nrequested_by: Magreth Mushi (magreth.jubilate@gmail.com)\n\nrequest_note: [experimenter] - role request\nrequested_date: 01/30/2023, 09:35:33\n\nreceived_by: ['AERPAW Admin', 'Dr Rudra Dutta (rdutta@ncsu.edu)', 'Ismail Guvenc (iguvenc@ncsu.edu)', 'Magreth Mushi (magreth.jubilate@gmail.com)', 'Michael J. Stealey', 'Mihai (NCSU)', 'Sudhanva Nagaragadde (snagara9@ncsu.edu)']\n\ncompleted_by: Dr Magreth Jubilate Mushi (mjmushi@ncsu.edu)\nis_approved: True\nresponse_note: Your request is approved. Welcome to AERPAW\nresponse_date: 01/30/2023, 09:45:36\n",
      "message_id": 132,
      "message_subject": "RESPONSE: [experimenter] - role request",
      "sent_by": 22,
      "sent_date": "2023-01-30T09:45:36.448022-05:00"
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/messages/212 ***
{
  "is_deleted": false,
  "is_read": false,
  "last_modified_by": 22,
  "message_body": "\nrequest_type: role\n\nrequested_by: Kwon HyeokJun\n\nrequest_note: [experimenter] - role request\nrequested_date: 01/31/2023, 15:28:32\n\nreceived_by: ['AERPAW Admin', 'Dr Rudra Dutta (rdutta@ncsu.edu)', 'Ismail Guvenc (iguvenc@ncsu.edu)', 'Kwon HyeokJun', 'Michael J. Stealey', 'Mihai (NCSU)', 'Sudhanva Nagaragadde (snagara9@ncsu.edu)']\n\ncompleted_by: Dr Magreth Jubilate Mushi (mjmushi@ncsu.edu)\nis_approved: True\nresponse_note: -----\nresponse_date: 01/31/2023, 15:39:57\n",
  "message_id": 212,
  "message_subject": "RESPONSE: [experimenter] - role request",
  "modified_date": "2023-01-31T15:39:57.453527-05:00",
  "received_by": [
    1,
    11,
    6,
    131,
    2,
    8,
    100
  ],
  "read_date": null,
  "sent_by": 22,
  "sent_date": "2023-01-31T15:39:57.447469-05:00"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** DELETE: https://127.0.0.1:8443/api/messages/212 ***
- Response: <Response [204]>
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


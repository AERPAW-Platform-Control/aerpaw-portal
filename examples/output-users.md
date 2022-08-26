Output observed from running the `users.py` script (credentials and tokens shortened for readability)

```console
$ python -m users

*** /users: paginated list of users ***
*** GET: http://127.0.0.1:8000/api/users ***
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "display_name": "Michael Stealey",
      "email": "stealey@unc.edu",
      "user_id": 1,
      "username": "stealey@unc.edu"
    }
  ]
}

*** /users?search=stea: paginated list of users with search ***
*** GET: http://127.0.0.1:8000/api/users?search=stea ***
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "display_name": "Michael Stealey",
      "email": "stealey@unc.edu",
      "user_id": 1,
      "username": "stealey@unc.edu"
    }
  ]
}

*** /users/{int:pk}: retrieve details for user with pk = 1 ***
*** GET: http://127.0.0.1:8000/api/users/1 ***
{
  "aerpaw_roles": [
    "experimenter",
    "pi",
    "operator",
    "site_admin"
  ],
  "display_name": "Michael Stealey",
  "email": "stealey@unc.edu",
  "is_active": true,
  "openid_sub": "http://cilogon.org/serverA/users/242181",
  "user_id": 1,
  "username": "stealey@unc.edu"
}

*** /users/{int:pk}: update "disoplay_name" for user with pk = 1 ***
*** PUT: http://127.0.0.1:8000/api/users/1 ***
{
  "aerpaw_roles": [
    "experimenter",
    "pi",
    "operator",
    "site_admin"
  ],
  "display_name": "Michael J. Stealey, Sr.",
  "email": "stealey@unc.edu",
  "is_active": true,
  "openid_sub": "http://cilogon.org/serverA/users/242181",
  "user_id": 1,
  "username": "stealey@unc.edu"
}

*** /users/{int:pk}/credentials: credentials for user with pk = 1 ***
*** GET: http://127.0.0.1:8000/api/users/1/credentials ***
[
  {
    "created_date": "2022-08-26T08:22:51.353415-04:00",
    "is_expired": false,
    "last_modified_by": "stealey@unc.edu",
    "modified_date": "2022-08-26T08:22:51.353429-04:00",
    "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCdS9SYWzMZba7w3jI/.../eAFHmxECSZN",
    "public_key_expiration": "2023-08-26T08:22:51.353180-04:00",
    "public_key_id": 1,
    "public_key_name": "credential one",
    "user_id": 1
  },
  {
    "created_date": "2022-08-26T08:23:11.152547-04:00",
    "is_expired": false,
    "last_modified_by": "stealey@unc.edu",
    "modified_date": "2022-08-26T08:23:11.152559-04:00",
    "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDWwN/.../S+kZhGHuERZTDz57Z",
    "public_key_expiration": "2023-08-26T08:23:11.152315-04:00",
    "public_key_id": 2,
    "public_key_name": "credential two",
    "user_id": 1
  }
]

*** /users/{int:pk}/tokens: retrieve tokens for user with pk = 1 ***
*** GET: http://127.0.0.1:8000/api/users/1/tokens ***
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...Zif4Jg00r3SzqFlpHXxFkaSIBq4v45g62SR6X--Vi0E",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...kbimneSIb1-IlPkoJ-ImRvjobUA-fCWN0Y5CufM1hr8"
}

*** /users/{int:pk}/tokens?refresh=true: refresh tokens for user with pk = 1 ***
*** GET: http://127.0.0.1:8000/api/users/1/tokens?refresh=true ***
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...8YkIDjb1LAkj8f7bHn7HRh21jlwuDzKzIMc1LSUoV9I",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...kbimneSIb1-IlPkoJ-ImRvjobUA-fCWN0Y5CufM1hr8"
}

*** /users/{int:pk}/tokens?generate=true: generate tokens for user with pk = 1 ***
*** GET: http://127.0.0.1:8000/api/users/1/tokens?generate=true ***
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...lZB_nTU3Uzwrm-iNOk9FLXfx_oyS28J0Wou-W9DemCA",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...mWuaoebhSB_K65l5vpO_WyhplmhFcehE3P8Ghp2O634"
}
```

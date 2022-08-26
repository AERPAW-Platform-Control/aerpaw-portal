Output observed from running the `users.py` script (credentials and tokens shortened for readability)

```console
$ python -m users

*** /users: paginated list of users ***
*** GET: http://aerpaw-dev.renci.org:8000/api/users ***
{
  "count": 7,
  "next": "http://aerpaw-dev.renci.org:8000/api/users?page=2",
  "previous": null,
  "results": [
    {
      "display_name": "Magreth Mushi",
      "email": "mjmushi@ncsu.edu",
      "user_id": 5,
      "username": "mjmushi@ncsu.edu"
    },
    {
      "display_name": "Michael Stealey",
      "email": "stealey@unc.edu",
      "user_id": 1,
      "username": "stealey@unc.edu"
    },
    {
      "display_name": "mj stealey",
      "email": "mjstealey@gmail.com",
      "user_id": 4,
      "username": "mjstealey@gmail.com"
    },
    {
      "display_name": "Rudra Dutta",
      "email": "rdutta@ncsu.edu",
      "user_id": 6,
      "username": "rdutta@ncsu.edu"
    },
    {
      "display_name": "Sonali Chaudhari",
      "email": "sschaud2@ncsu.edu",
      "user_id": 2,
      "username": "sschaud2@ncsu.edu"
    }
  ]
}

*** /users?search=stea: paginated list of users with search ***
*** GET: http://aerpaw-dev.renci.org:8000/api/users?search=stea ***
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "display_name": "Michael Stealey",
      "email": "stealey@unc.edu",
      "user_id": 1,
      "username": "stealey@unc.edu"
    },
    {
      "display_name": "mj stealey",
      "email": "mjstealey@gmail.com",
      "user_id": 4,
      "username": "mjstealey@gmail.com"
    }
  ]
}

*** /users/{int:pk}: retrieve details for user with pk = 1 ***
*** GET: http://aerpaw-dev.renci.org:8000/api/users/1 ***
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

*** /users/{int:pk}: update "display_name" for user with pk = 1 ***
*** data = {"display_name": "Michael J. Stealey, Sr."} ***
*** PUT: http://aerpaw-dev.renci.org:8000/api/users/1 ***
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
*** GET: http://aerpaw-dev.renci.org:8000/api/users/1/credentials ***
[
  {
    "created_date": "2022-08-11T15:20:31.025854-04:00",
    "is_expired": false,
    "last_modified_by": "stealey@unc.edu",
    "modified_date": "2022-08-11T15:20:31.025877-04:00",
    "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDV1TKBKVwbhNoTAdFf/.../FmTciZ8N7HgeOzLyw1hI4weL3W1bMDROEtdXQG7vAJoOT2svnkeWKcBsP1f6BCymVCZ9gBoJDBYwry9",
    "public_key_expiration": "2023-08-11T09:18:25.083517-04:00",
    "public_key_id": 3,
    "public_key_name": "me providing a key to use for something",
    "user_id": 1
  },
  {
    "created_date": "2022-08-11T15:18:34.285984-04:00",
    "is_expired": false,
    "last_modified_by": "stealey@unc.edu",
    "modified_date": "2022-08-11T15:18:34.286007-04:00",
    "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDLDutUA59lFQ9qzVYqUxWqthrlHHCRS61jirdcw7y6ry14iCb8ne4IJssxrB+TrBFyXOZr4WxGtG/.../+Jbp7HeqyiITooEWwaxOE4aixcn3l9UZgyyLnfkLnKSKOoeIhZFPLAUdz",
    "public_key_expiration": "2023-08-11T09:18:25.083517-04:00",
    "public_key_id": 2,
    "public_key_name": "some kind of name",
    "user_id": 1
  }
]

*** /users/{int:pk}/tokens: retrieve tokens for user with pk = 1 ***
*** GET: http://aerpaw-dev.renci.org:8000/api/users/1/tokens ***
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...mIlwbwiBRWcSwBKqjK2tyWollpUtU7Iv2Vso1Je7JZ4",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...1kxMijzzby4eY3uA-zAxE87E2tnYIGKlMgh9sWTZ3Bc"
}

*** /users/{int:pk}/tokens?refresh=true: refresh tokens for user with pk = 1 ***
*** GET: http://aerpaw-dev.renci.org:8000/api/users/1/tokens?refresh=true ***
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...6HmiC-kIWX7H9WCOyc2kfttCo5iYz2XvnXEmG4NBAp8",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...1kxMijzzby4eY3uA-zAxE87E2tnYIGKlMgh9sWTZ3Bc"
}

*** /users/{int:pk}/tokens?generate=true: generate tokens for user with pk = 1 ***
*** GET: http://aerpaw-dev.renci.org:8000/api/users/1/tokens?generate=true ***
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...j6_8keXYGwPRzvhbtb6r2Trg3LLFYVtco-41j6m0StI",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...j22nUFi8noclLnULYNnEt3WEIgArXx4UQV7ym02Mvv4"
}
```

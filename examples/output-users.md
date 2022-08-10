Output observed from running the `users.py` script

```console
$ python -m users

*** /users: paginated list with search***
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

*** /users/{int:pk}: detail for single user ***
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

*** /users/{int:pk}/credentials: list of user credentials ***
*** GET: http://aerpaw-dev.renci.org:8000/api/users/1/credentials ***
{}

*** /users/{int:pk}/tokens: user tokens ***
*** GET: http://aerpaw-dev.renci.org:8000/api/users/1/tokens ***
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...qsP5zZIbDrcA4zW6Xw8q4nV3fRz6XeVDg8MrfRij3xE",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...8si595TTlwAVxhEfOVZq9wNoSNCNdmzDsRr3yHwbPZQ"
}

*** /token/refresh/: refresh user access_token ***
*** POST: http://aerpaw-dev.renci.org:8000/api/token/refresh/ ***
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...1OIhf5-1M89SN3H-TeDs-e20DirciplWXptNT1t5rDE"
}
```

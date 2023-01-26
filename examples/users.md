## API `/users`

**Note**: User objects are created when a new user logs into the AERPAW portal for the first time and are not available
to be created via the API directly

### Endpoints

**`/users`**

- GET: paginated list of users

**`/users?search=<string>`**

- GET: paginated list of users where `<string>` is used as a search term against `display_name` and `email`

**`/users/{int:pk}`**

- GET: retrieve a single user by `user_id`
- PUT: update a single user by `user_id`
    - data optional: `display_name` as string

**`/users/{int:pk}/credentials`**

- GET: retrieve credentials for user by `user_id`

**`/users/{int:pk}/profile`**

- GET: retrieve profile for user by `user_id`
- PUT: update a single user profile by `user_id`
    - data optional: `employer` as string
    - data optional: `position` as string
    - data optional: `research_field` as string

**`/users/{int:pk}/tokens`**

- GET: retrieve tokens for user by `user_id`

**`/users/{int:pk}/tokens?refresh=true`**

- GET: retrieve updated `access_token` for user by `user_id`

**`/users/{int:pk}/tokens?generate=true`**

- GET: retrieve newly generated `access_token` and `refresh_token` for user by `user_id`

### Example Code

From [code/users.py](./code/users.py)

```python
if __name__ == '__main__':
    get_users_list()
    get_users_list_search()
    get_users_detail()
    put_users_detail()
    get_users_detail_credentials()
    get_users_detail_profile()
    put_users_detail_profile()
    get_users_detail_tokens()
    get_users_detail_tokens_refresh()
    get_users_detail_tokens_generate()
```

### Output from example code

Output observed from running the `users.py` script (credentials and tokens shortened for readability)

```console
(venv)$ python -m users
*** GET: https://127.0.0.1:8443/api/users ***
{
  "count": 126,
  "next": "https://127.0.0.1:8443/api/users?page=2",
  "previous": null,
  "results": [
    {
      "display_name": "",
      "email": "christianj@uchicago.edu",
      "user_id": 112,
      "username": "christianj@uchicago.edu"
    },
    {
      "display_name": " (852012393@qq.com)",
      "email": "852012393@qq.com",
      "user_id": 122,
      "username": "852012393@qq.com"
    },
    ...
    {
      "display_name": "agurses",
      "email": "agurses@ncsu.edu",
      "user_id": 21,
      "username": "agurses@ncsu.edu"
    },
    {
      "display_name": "Ahmed Hussain (ahmedhussain.85@gmail.com)",
      "email": "ahmedhussain.85@gmail.com",
      "user_id": 71,
      "username": "ahmedhussain.85@gmail.com"
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/users?search=stea ***
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "display_name": "Michael Stealey",
      "email": "stealey@unc.edu",
      "user_id": 2,
      "username": "stealey@unc.edu"
    },
    {
      "display_name": "mj stealey (mjstealey@gmail.com)",
      "email": "mjstealey@gmail.com",
      "user_id": 15,
      "username": "mjstealey@gmail.com"
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/users/2 ***
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
  "user_id": 2,
  "username": "stealey@unc.edu"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** PUT: https://127.0.0.1:8443/api/users/2 ***
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
  "user_id": 2,
  "username": "stealey@unc.edu"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/users/2/credentials ***
[
  {
    "created_date": "2023-01-25T08:54:47.917949-05:00",
    "is_expired": false,
    "last_modified_by": "stealey@unc.edu",
    "modified_date": "2023-01-25T08:54:47.917959-05:00",
    "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABA...CdyQAUVxI6JMndd+MCT6cgc4VFkhzF",
    "public_key_expiration": "2024-01-25T08:54:47.917711-05:00",
    "public_key_id": 65,
    "public_key_name": "aerpaw-ssh-key",
    "user_id": 2
  }
]
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

{"employer":null,"position":null,"research_field":null}
*** GET: https://127.0.0.1:8443/api/users/2/profile ***
{
  "employer": null,
  "position": null,
  "research_field": null
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** TODO: PUT: https://127.0.0.1:8443/api/users/2/profile ***
{
  "detail": "Method \"PUT\" not allowed."
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/users/2/tokens ***
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..UQfv9v0S7J0rn1Tc1cOThrysY2ME7JbGdHi0vhVoyg0",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..jqGW_KRe5oihw2Xgl6dAdGZ9ajVYusBPNQpzqhthGRo"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/users/2/tokens?refresh=true ***
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..SAk6hZ44ohlwuQulO5N6vNflW8BgnPZFit-vkCplEo4",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..jqGW_KRe5oihw2Xgl6dAdGZ9ajVYusBPNQpzqhthGRo"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/users/2/tokens?generate=true ***
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..MqNU_RR_NXo0XdE5WIVi71c2spiVA53IYQaAzUQZk3Y",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..vyogqy-H8ObRtKGA_Aq4feTi488Qy15lZRyQiYGgrhU"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


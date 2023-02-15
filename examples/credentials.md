## API `/credentials`

**Note**: regarding creating a new credenial 

- The user can upload a pre-existing **public_key_credential** which is saved to the database OR
- The user can generate a new credential wher both the **public_key** and **private_key** is returned to the user, but only the **public_key_credential** is saved to the database. The user **MUST** retrieve the **private_key** at the time of creation as it will not be shown again. 

```
POST: create new credential
- public_key_credential  - string (optional - when not present a new key is generated)
- public_key_name        - string (required)
```

### Endpoints

**`/credentials`**

- GET: paginated list of credentials
  - if user is `operator` all credentials are returned
  - is user is not `operator` only self credentials are returned
- POST: create new credential
  - data optional: `public_key_credential` as string - when not present a new key is generated
  - data required: `public_key_name` as string

**`/credentials?user_id=<int>`**

- GET: paginated list of credentials where `<int>` is used to search for a specific User by `user_id`
  - if user is `operator` all matching credentials are returned
  - is user is not `operator` only self matching credentials are returned

**`/credentials/{int:pk}`**

- GET: retrieve a single credential by `public_key_id`
  - if user is `operator` all matching credentials are returned
  - is user is not `operator` only self matching credentials are returned
- PUT: update a single user by `public_key_id `
    - data optional: `public_key_name` as string

**`/credentials/{int:pk}`**

- DELETE: soft delete credential by `public_key_id `

### Example Code

From [code/credentials.py](./code/credentials.py)

```python
if __name__ == '__main__':
    get_credentials_list()
    post_credentials_create()
    get_credentials_list_search()
    get_credentials_detail()
    put_credentials_detail()
    delete_credentials_detail()
```

### Output from example code

Output observed from running the `credentials.py` script

```console
(venv)$ python -m credentials
*** GET: https://127.0.0.1:8443/api/credentials ***
{
  "count": 65,
  "next": "https://127.0.0.1:8443/api/credentials?page=2",
  "previous": null,
  "results": [
    {
      "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDeJkR6os...VCcRbpyuQhBDalOBiDAF08YapRwWxlVU9KSyVQnw9D1dnWl11",
      "public_key_expiration": "2024-01-29T08:05:36.997482-05:00",
      "public_key_id": 65,
      "public_key_name": "demo key name for testing purposes",
      "user_id": 2
    },
    {
      "public_key_credential": "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQ...nqbXcaU89anj07wAAABA4NTIwMTIzOTNAcXEuY29tAQIDBA==",
      "public_key_expiration": "2023-12-25T13:01:52.100000-05:00",
      "public_key_id": 64,
      "public_key_name": "852012393@qq.com publickey",
      "user_id": 122
    },
    ...
    {
      "public_key_credential": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5...k58odCuPc3O+sBtFE niall.p.mullane@gmail.com",
      "public_key_expiration": "2023-12-25T13:01:52.100000-05:00",
      "public_key_id": 57,
      "public_key_name": "npmullan@ncsu.edu publickey",
      "user_id": 94
    },
    {
      "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAA...QC7VGsAtB3A5FYLB1x1Hew7Y6H8XSktrKqYfo1PRLWUhN",
      "public_key_expiration": "2023-12-25T13:01:52.100000-05:00",
      "public_key_id": 56,
      "public_key_name": "aerpawdemo@gmail.com publickey",
      "user_id": 93
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** POST: https://127.0.0.1:8443/api/credentials ***
{
  "created_date": "2023-01-29T08:21:54.222898-05:00",
  "is_expired": false,
  "last_modified_by": "stealey@unc.edu",
  "modified_date": "2023-01-29T08:21:54.222909-05:00",
  "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSDUUA...VPgUeTdQXbPm5V2tGvAfkhj65XxcT1MJcciQb",
  "public_key_expiration": "2024-01-29T08:21:54.222725-05:00",
  "public_key_id": 67,
  "public_key_name": "demo key name for testing purposes",
  "user_id": 2,
  "private_key_credential": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA...xXStKijSe2KpSQ\n-----END RSA PRIVATE KEY-----\n"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/credentials?user_id=22 ***
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCPibCM...B3A5FYLB1x1Hew7Y6H8XSktrKqYfo1PRLWUhN rsa-key-20210915",
      "public_key_expiration": "2023-12-25T13:01:52.100000-05:00",
      "public_key_id": 12,
      "public_key_name": "mjmushi@ncsu.edu publickey",
      "user_id": 22
    }
  ]
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** GET: https://127.0.0.1:8443/api/credentials/67 ***
{
  "created_date": "2023-01-29T08:21:54.222898-05:00",
  "is_expired": false,
  "last_modified_by": "stealey@unc.edu",
  "modified_date": "2023-01-29T08:21:54.222909-05:00",
  "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSDUUA...VPgUeTdQXbPm5V2tGvAfkhj65XxcT1MJcciQb",
  "public_key_expiration": "2024-01-29T08:21:54.222725-05:00",
  "public_key_id": 67,
  "public_key_name": "demo key name for testing purposes",
  "user_id": 2
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** PUT: https://127.0.0.1:8443/api/credentials/67 ***
{
  "created_date": "2023-01-29T08:21:54.222898-05:00",
  "is_expired": false,
  "last_modified_by": "stealey@unc.edu",
  "modified_date": "2023-01-29T08:21:54.316805-05:00",
  "public_key_credential": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSDUUA...VPgUeTdQXbPm5V2tGvAfkhj65XxcT1MJcciQb",
  "public_key_expiration": "2024-01-29T08:21:54.222725-05:00",
  "public_key_id": 67,
  "public_key_name": "update demo key name for testing purposes",
  "user_id": 2
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

*** DELETE: https://127.0.0.1:8443/api/credentials/67 ***
- Response: <Response [204]>
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


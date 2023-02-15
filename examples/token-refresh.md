## API `/token-refresh`

**Note**: This applies primarily to script based interaction with the API where the user would refresh the access token as part of their script

- A valid `access_token` is not required, only a valid `refresh_token` to generate a new `access_token`

### Endpoints

**`/token/refresh/`**

- POST: refresh access_token using a valid refresh_token
  - required data: `refresh` as string - valid refresh token

### Example Code

From [code/token-refresh.py](./code/token-refresh.py)

```python
if __name__ == '__main__':
    post_token_refresh()
```

### Output from example code

Output observed from running the `user-project.py` script

```console
(venv)$ python -m token-refresh
*** POST: https://127.0.0.1:8443/api/token/refresh/ ***
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...fK6dG_M5tnpYaeoU4XYf_xUAEXD0Za7IWMaWVlfsjpA"
}
*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
```


# Configure

The configuration below is the minimum required to establish a running instance of the Portal. For a more detailed overview of the settings see [Configuration Files](./configuration-files.md)

## Choose your mode of operation

The portal can be run in three different modes depending on your use case

1. [Local Development - HTTP](#local-dev) (`local-dev`)
2. [Local Development - with SSL](#local-ssl) (`local-ssl`)
3. [Production - all in Docker](#in-docker) (`docker`)

## 1. <a name="local-dev"></a>Local Development - HTTP

Overview:

- Portal - Django runs locally on port 8000 (host)
- Database - Postgres runs in docker on port 5432 (host/docker)

### file: `docker-compose.yml`

Copy the `.local-dev` version to the main level of the repository as `docker-compose.yml`

```
cp compose/docker-compose.yml.local-dev ./docker-compose.yml
```

### file: `.env`

Copy the `env.template` file to the main level of the repository as `.env`

```
cp env.template ./.env
```

Modify the lines denoted below

```env
...
# AERPAW Ops settings
export AERPAW_OPS_MOCK=true                                     # <-- mock calls to AERPAW Ops server (true/false)
...
export AERPAW_OPS_PORTAL_PASSWORD='xxxxxxxxxx'                  # <-- password used by fn: create_aerpaw_admin_user
...

# Django settings
...
export DJANGO_SECRET_KEY='xxxxxxxxxx'                           # <-- Django secret key, e.g. https://django-secret-key-generator.netlify.app
...

# OIDC CILogon - values provided when OIDC client is created
# callback url
export OIDC_RP_CALLBACK='http://127.0.0.1:8000/oidc/callback/'  # <-- Callback URL as registered with CILogon
# client id and client secret
export OIDC_RP_CLIENT_ID='xxxxxxxxxx'                           # <-- OIDC Client ID as registered with CILogon
export OIDC_RP_CLIENT_SECRET='xxxxxxxxxx'                       # <-- OIDC Client Secret as registered with CILogon
...

# PostgreSQL database - default values should not be used in production
...
export POSTGRES_PASSWORD=xxxxxxxxxx                             # <-- Postgres password for database
...
```

The above configuration represents the minimum required to establish a running instance of the Portal. For a more detailed overview of the settings see [Configuration Files](./configuration-files.md)

Continue onto [Deploy](./deploy.md)

## 2. <a name="local-ssl"></a>Local Development - with SSL

Overview:

- Portal - Django runs locally on port 8000 (host)
- Database - Postgres runs in docker on port 5432 (host/docker)
- Webserver - Nginx runs in docker on ports 8080, 8443 (host/docker)

### file: `docker-compose.yml`

Copy the `.local-ssl` version to the main level of the repository as `docker-compose.yml`

```
cp compose/docker-compose.yml.local-dev ./docker-compose.yml
```

### file: `.env`

Copy the `env.template` file to the main level of the repository as `.env`

```
cp env.template ./.env
```

Modify the lines denoted below

```env
...
# AERPAW Ops settings
export AERPAW_OPS_MOCK=true                                     # <-- mock calls to AERPAW Ops server (true/false)
...
export AERPAW_OPS_PORTAL_PASSWORD='xxxxxxxxxx'                  # <-- password used by fn: create_aerpaw_admin_user
...

# Django settings
...
export DJANGO_SECRET_KEY='xxxxxxxxxx'                           # <-- Django secret key, e.g. https://django-secret-key-generator.netlify.app
...

# OIDC CILogon - values provided when OIDC client is created
# callback url
export OIDC_RP_CALLBACK='https://127.0.0.1:8443/oidc/callback/' # <-- Callback URL as registered with CILogon
# client id and client secret
export OIDC_RP_CLIENT_ID='xxxxxxxxxx'                           # <-- OIDC Client ID as registered with CILogon
export OIDC_RP_CLIENT_SECRET='xxxxxxxxxx'                       # <-- OIDC Client Secret as registered with CILogon
...

# PostgreSQL database - default values should not be used in production
...
export POSTGRES_PASSWORD=xxxxxxxxxx                             # <-- Postgres password for database
...
```

The above configuration represents the minimum required to establish a running instance of the Portal. For a more detailed overview of the settings see [Configuration Files](./configuration-files.md)

Continue onto [Deploy](./deploy.md)

## 3. <a name="in-docker"></a>Production - all in Docker

Overview:

- Portal - Django runs in docker on port 8000 (docker)
- Database - Postgres runs in docker on port 5432 (docker)
- Webserver - Nginx runs in docker on ports 8080, 8443 (host/docker)

### file: `docker-compose.yml`

Copy the `.local-ssl` version to the main level of the repository as `docker-compose.yml`

```
cp compose/docker-compose.yml.docker ./docker-compose.yml
```

### file: `.env`

Copy the `env.template` file to the main level of the repository as `.env`

```
cp env.template ./.env
```

Modify lines

```env
...
# AERPAW Ops settings
export AERPAW_OPS_MOCK=true                                     # <-- mock calls to AERPAW Ops server (true/false)
...
export AERPAW_OPS_PORTAL_PASSWORD='xxxxxxxxxx'                  # <-- password used by fn: create_aerpaw_admin_user
...

# Django settings
...
export DJANGO_SECRET_KEY='xxxxxxxxxx'                           # <-- Django secret key, e.g. https://django-secret-key-generator.netlify.app
...

# OIDC CILogon - values provided when OIDC client is created
# callback url
export OIDC_RP_CALLBACK='https://127.0.0.1:8443/oidc/callback/' # <-- Callback URL as registered with CILogon
# client id and client secret
export OIDC_RP_CLIENT_ID='xxxxxxxxxx'                           # <-- OIDC Client ID as registered with CILogon
export OIDC_RP_CLIENT_SECRET='xxxxxxxxxx'                       # <-- OIDC Client Secret as registered with CILogon
...

# PostgreSQL database - default values should not be used in production
...
export POSTGRES_HOST=portal-databse                             # <-- FQDN / IP / Name of database container
...
export POSTGRES_PASSWORD=xxxxxxxxxx                             # <-- Postgres password for database
...

# uWSGI services in Django
export UWSGI_GID=1000                                           # <-- GID of user running services on HOST, e.g. id -g
export UWSGI_UID=1000                                           # <-- UID of user running services on HOST, e.g. id -u
```

### file: `nginx/default.conf`

Modify the `default.conf` file in place

```env
# the upstream component nginx needs to connect to
upstream django {
    # use for local-ssl deployment
    # server host.docker.internal:8000; # TCP socket            # <-- comment this line
    # use for docker deployment
    server portal-django:8000;                                  # <-- uncomment this line
}
...
```

The above configuration represents the minimum required to establish a running instance of the Portal. For a more detailed overview of the settings see [Configuration Files](./configuration-files.md)

Continue onto [Deploy](./deploy.md)

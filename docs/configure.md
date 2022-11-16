# Configure

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

Modify lines

```env
...
# AERPAW Ops settings
export AERPAW_OPS_MOCK=true                                     # <-- true - leave this as it is
...
export AERPAW_OPS_PORTAL_PASSWORD='xxxxxxxxxx'                  # <-- user defined

# Django settings
...
export DJANGO_SECRET_KEY='xxxxxxxxxx'                           # <-- user defined, e.g. https://django-secret-key-generator.netlify.app  

# OIDC CILogon - values provided when OIDC client is created
# callback url
export OIDC_RP_CALLBACK='http://127.0.0.1:8000/oidc/callback/'  # <-- registered callback URL in CILogon
# client id and client secret
export OIDC_RP_CLIENT_ID='xxxxxxxxxx'                           # <-- from CILogon OIDC Client
export OIDC_RP_CLIENT_SECRET='xxxxxxxxxx'                       # <-- from CILogon OIDC Client
...

# PostgreSQL database - default values should not be used in production
export HOST_DB_DATA=./db_data
...
export POSTGRES_PASSWORD=xxxxxxxxxx                             # <-- user defined
...
```

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

Modify lines

```env
...
# AERPAW Ops settings
export AERPAW_OPS_MOCK=true                                     # <-- true - leave this as it is
...
export AERPAW_OPS_PORTAL_PASSWORD='xxxxxxxxxx'                  # <-- user defined

# Django settings
...
export DJANGO_SECRET_KEY='xxxxxxxxxx'                           # <-- user defined, e.g. https://django-secret-key-generator.netlify.app  

# OIDC CILogon - values provided when OIDC client is created
# callback url
export OIDC_RP_CALLBACK='https://127.0.0.1:8443/oidc/callback/' # <-- registered callback URL in CILogon
# client id and client secret
export OIDC_RP_CLIENT_ID='xxxxxxxxxx'                           # <-- from CILogon OIDC Client
export OIDC_RP_CLIENT_SECRET='xxxxxxxxxx'                       # <-- from CILogon OIDC Client
...

# PostgreSQL database - default values should not be used in production
export HOST_DB_DATA=./db_data
...
export POSTGRES_PASSWORD=xxxxxxxxxx                             # <-- user defined
...
```

Continue onto [Deploy](./deploy.md)

## 3. <a name="in-docker"></a>Production - all in Docker

Overview:

- Portal - Django runs in docker on port 8000 (docker)
- Database - Postgres runs in docker on port 5432 (docker)
- Webserver - Nginx runs in docker on ports 8080, 8443 (host/docker)


Continue onto [Deploy](./deploy.md)

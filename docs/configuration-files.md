# Configuration Files

## file: `docker-compose.yml`

Default file is based on Local Development - HTTP mode, other versions are found in the `/compose` directory

- make a copy of this file as `docker-compose.yml` before editing

```yaml
# compose/docker-compose.yml.local-dev
# - database port 5432 exposed to host (security risk)

version: '3.9'
services:

  database:
    # default port 5432
    image: postgres:14
    container_name: portal-database
    networks:
      - portal-network
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      PGDATA: ${PGDATA}
#    volumes:
#      - ${HOST_DB_DATA}:/var/lib/postgresql/data
    restart: unless-stopped

networks:
  portal-network:
    name: portal-network
    driver: bridge
```

## file: `.env`

A template environment file named `template.env` is provided as the basis for your `.env` file

- make a copy of this file as `.env` before editing

```env
# docker-compose environment file
#
# When you set the same environment variable in multiple files,
# here’s the priority used by Compose to choose which value to use:
#
#  1. Compose file
#  2. Shell environment variables
#  3. Environment file
#  4. Dockerfile
#  5. Variable is not defined

# AERPAW Ops settings
export AERPAW_OPS_MOCK=true                                     # <-- mock calls to AERPAW Ops server (true/false)
export AERPAW_OPS_HOST='xxxxxxxxxx'                             # <-- FQDN or IP of AERPAW Ops server
export AERPAW_OPS_PORT=22
export AERPAW_OPS_USER='xxxxxxxxxx'                             # <-- AERPAW Ops service username
export AERPAW_OPS_KEY_FILE='./ssh/demo_id_rsa'                  # <-- AERPAW Ops service private key
export AERPAW_OPS_PORTAL_USERNAME='demo_admin@gmail.com'        # <-- username used by fn: create_aerpaw_admin_user
export AERPAW_OPS_PORTAL_PASSWORD='xxxxxxxxxx'                  # <-- password used by fn: create_aerpaw_admin_user

# AERPAW Email settings - gmail as example
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER='demo_admin@gmail.com'                   # <-- Email username - can be different than AERPAW_OPS_PORTAL_USERNAME
export EMAIL_HOST_PASSWORD='xxxxxxxxxx'                         # <-- Email password
export EMAIL_ADMIN_USER='demo_admin@gmail.com'                  # <-- Email username - can be different than AERPAW_OPS_PORTAL_USERNAME

# Django settings
export PYTHONPATH=./:./venv:./.venv
export DJANGO_ALLOWED_HOSTS='127.0.0.1'                         # <-- FQDN or IP of Portal
export DJANGO_SECRET_KEY='xxxxxxxxxx'                           # <-- Django secret key, e.g. https://django-secret-key-generator.netlify.app
export DJANGO_DEBUG=true                                        # <-- Django DEBUG mode (true/false)
export DJANGO_LOG_LEVEL='DEBUG'
export DJANGO_SESSION_COOKIE_AGE='14400'
export DJANGO_TIME_ZONE='America/New_York'

# Bearer Token
export ACCESS_TOKEN_LIFETIME_HOURS=24
export REFRESH_TOKEN_LIFETIME_DAYS=30

# Nginx configuration
export NGINX_DEFAULT_CONF=./nginx/default.conf
export NGINX_NGINX_CONF=./nginx/nginx.conf
export NGINX_SSL_CERTS_DIR=./ssl                                # <-- HOST path to SSL certificates

# OIDC CILogon - values provided when OIDC client is created
# callback url
export OIDC_RP_CALLBACK='http://127.0.0.1:8000/oidc/callback/'  # <-- Callback URL as registered with CILogon
# client id and client secret
export OIDC_RP_CLIENT_ID='xxxxxxxxxx'                           # <-- OIDC Client ID as registered with CILogon
export OIDC_RP_CLIENT_SECRET='xxxxxxxxxx'                       # <-- OIDC Client Secret as registered with CILogon
# oidc scopes
export OIDC_RP_SCOPES="openid email profile org.cilogon.userinfo"
# signing algorithm
export OIDC_RP_SIGN_ALGO='RS256'
export OIDC_OP_JWKS_ENDPOINT='https://cilogon.org/oauth2/certs'
# OpenID Connect provider
export OIDC_OP_AUTHORIZATION_ENDPOINT='https://cilogon.org/authorize'
export OIDC_OP_TOKEN_ENDPOINT='https://cilogon.org/oauth2/token'
export OIDC_OP_USER_ENDPOINT='https://cilogon.org/oauth2/userinfo'
# session renewal period (in seconds)
export OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS=3600

export OIDC_STORE_ACCESS_TOKEN=true
export OIDC_STORE_ID_TOKEN=true
export OIDC_LOGOUT_URL='https://cilogon.org/logout'
export OIDC_OP_LOGOUT_URL_METHOD='main.openid.logout'

# PostgreSQL database - default values should not be used in production
export HOST_DB_DATA=./db_data                                   # <-- HOST path to database storage
export PGDATA=/var/lib/postgresql/data                          # <-- Container path to database storage
export POSTGRES_HOST=127.0.0.1                                  # <-- FQDN / IP / Name of database container
export POSTGRES_DB=postgres
export POSTGRES_PASSWORD=xxxxxxxxxx                             # <-- Postgres password for database
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres

# uWSGI services in Django
export UWSGI_GID=1000                                           # <-- GID of user running services on HOST, e.g. id -g
export UWSGI_UID=1000                                           # <-- UID of user running services on HOST, e.g. id -u
```

## file: `nginx/default.conf`

Default based on Local Development - with SSL mode

- edit this file in place

```env
# the upstream component nginx needs to connect to
upstream django {
    # use for local-ssl deployment
    server host.docker.internal:8000; # TCP socket
    # use for docker deployment
    # server portal-django:8000;
}

server {
    listen 80;
    return 301 https://$host:8443$request_uri; # substitute your machine's FQDN or IP address and port
 match your setup
}

server {
    listen   443 ssl default_server;
    # the domain name it will serve for
    server_name $host:8443; # substitute your machine's FQDN or IP address and port

    # If they come here using HTTP, bounce them to the correct scheme
    error_page 497 https://$server_name$request_uri;
    # Or if you're on the default port 443, then this should work too
    # error_page 497 https://;

    # Let's Encrypt format - match what's on your machine
    ssl_certificate           /etc/ssl/fullchain.pem;
    ssl_certificate_key       /etc/ssl/privkey.pem;
    ssl_trusted_certificate   /etc/ssl/chain.pem;

    charset     utf-8;

    # max upload size
    client_max_body_size 75M;   # adjust to taste

    # Cache configuration
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 5;
    open_file_cache_errors off;

    # Django media
    location /media  {
        alias /code/portal/media;  # your Django project's media files - amend as required
    }

    location /static {
        alias /code/portal/static; # your Django project's static files - amend as required
    }

    # Finally, send all non-media requests to the Django server.
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Host $http_host;
        proxy_redirect off;

        proxy_buffers 8 24k;
        proxy_buffer_size 2k;
        uwsgi_pass  django;
        include     /code/uwsgi_params; # the uwsgi_params file
    }
}
```

# AERPAW Portal

**WORK IN PROGRESS**

Phase-2 refactoring of [original AERPAW Portal](https://github.com/AERPAW-Platform-Control/portal) aimed at addressing feedback from Phase-1 and migrating services to be ReST API based.

- Refactored ORM and data table design ([Django](https://docs.djangoproject.com/en/4.0/))
- ReSTful API interface ([Django ReST Framework](https://www.django-rest-framework.org))
- Token based (JWT) authentication and authorization for remote API use ([djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/))
- Django views / templates populated via the API

**DISCLAIMER: The code herein may not be up to date nor compliant with the most recent package and/or security notices. The frequency at which this code is reviewed and updated is based solely on the lifecycle of the project for which it was written to support, and is not actively maintained outside of that scope. Use at your own risk.**

### Requirements

- Docker: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
- Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
- Python 3.9+: [https://www.python.org](https://www.python.org)

The Python environment illustrated in this document is deployed using `virtualenv` ([https://virtualenv.pypa.io/en/latest/](https://virtualenv.pypa.io/en/latest/)). You are welcome to use whichever environment you are most comfortable with.

### Operational modes

The portal can be run in three different modes depending on your use case

1. **Local Development - HTTP** (`local-dev`)
  - database: Postgres container running in Docker (port `5432:5432`)
  - portal: Django with development server running on the host (port `8000`)
2. **Local Development - with SSL** (`local-ssl`)
  - database: Postgres container running in Docker (port `5432:5432`)
  - nginx: Webserver container running in Docker with self-signed SSL certificates (ports `8080:80`, `8443:443`)
  - portal: Django with uWSGI server running on the host (port `8000`)
3. **Production - all in Docker** (`docker`)
  - database: Postgres container running in Docker (port `N/A:5432`)
  - nginx: Webserver container running in Docker with user defined SSL certificates (ports `80:80`, `443:443`)
  - portal: Django with uWSGI server running in Docker (port `N/A:8000`)

## Table of Contents

- [Configure](./docs/configure.md) - configuration settings for each deployment mode
  - [Configuration Files](./docs/configuration-files.md) - overview of the configuration files used for deployment
- [Deploy](./docs/deploy.md) - deployment steps for each mode
- [First Run](./docs/first-run.md) - setting up the first administrative user
- [Database Backup and Restore](./docs/db-backup-restore.md) - how to backup and restore the database using fixtures

### Administrators/Operators

- [Production Overview](./docs/production-overview.md)

### Developers

- [Example code in Python](./examples/README.md)
- [API brief overview](./API_ENDPOINTS.md)

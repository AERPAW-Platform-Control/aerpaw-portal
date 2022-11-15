# AERPAW Portal

**WORK IN PROGRESS**

Phase-2 refactoring of [original AERPAW Portal](https://github.com/AERPAW-Platform-Control/portal) aimed at addressing feedback from Phase-1.

- Refactored ORM and data table design ([Django](https://docs.djangoproject.com/en/4.0/))
- ReSTful API interface ([Django ReST Framework](https://www.django-rest-framework.org))
- Token based (JWT) authentication and authorization for remote API use ([djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/))
- Django views / templates populated via the API

**DISCLAIMER: The code herein may not be up to date nor compliant with the most recent package and/or security notices. The frequency at which this code is reviewed and updated is based solely on the lifecycle of the project for which it was written to support, and is not actively maintained outside of that scope. Use at your own risk.**

### <a name="requirments"></a>Requirements

- Docker: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
- Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
- Python 3.9+: [https://www.python.org](https://www.python.org)

The Python environment illustrated in this document is deployed using `virtualenv` ([https://virtualenv.pypa.io/en/latest/](https://virtualenv.pypa.io/en/latest/)). You are welcome to use whichever environment you are most comfortable with.

## Table of Contents

- [Configuration Files](./docs/configuration-files.md)
- [Configure](./docs/configure.md)
- [Deploy](./docs/deploy.md)
- [First Run](./docs/first-run.md)
- [Database Backup and Restore](./docs/db-backup-restore.md)

### Old

- [Installation](./INSTALL.md)
- [Usage](./USAGE.md)
- [Example code in Python](./examples/README.md)
- [API brief overview](./API_ENDPOINTS.md)
- [Documentation](./docs/README.md)

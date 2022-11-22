# Database Backup and Restore

This document explains how to backup and restore the Postgres database using fixture files.

## Backup the data as fixture files

### Directory `dumpdata` and script `dumpdata.sh`

There is a persistent directory named `dumpdata` at the main level of the repository along with a script named `dumpdata.sh`

As one might guess running the script will extract fixture data and save it into the dumpdata directory.

The script will be invoked differently depending on whether the Portal is being run locally or in a Docker container.

### Local Development

Run the `dumpdata.sh` script (must have active virtual environment and sourced the environment variables prior to running script)

```console
./dumpdata.sh
```

Example output:

```console
$ ./dumpdata.sh
python3 ./manage.py dumpdata credentials --indent 2 --output ./dumpdata/credentials.json
[...........................................................................]
python3 ./manage.py dumpdata experiment_files --indent 2 --output ./dumpdata/experiment_files.json
[...........................................................................]
python3 ./manage.py dumpdata experiments --indent 2 --output ./dumpdata/experiments.json
[...........................................................................]
python3 ./manage.py dumpdata operations --indent 2 --output ./dumpdata/operations.json
[...........................................................................]
python3 ./manage.py dumpdata profiles --indent 2 --output ./dumpdata/profiles.json
[...........................................................................]
python3 ./manage.py dumpdata projects --indent 2 --output ./dumpdata/projects.json
[...........................................................................]
python3 ./manage.py dumpdata resources --indent 2 --output ./dumpdata/resources.json
[...........................................................................]
python3 ./manage.py dumpdata user_messages --indent 2 --output ./dumpdata/user_messages.json
python3 ./manage.py dumpdata user_requests --indent 2 --output ./dumpdata/user_requests.json
[...........................................................................]
python3 ./manage.py dumpdata users --indent 2 --output ./dumpdata/users.json
[...........................................................................]
```

### In Docker

```console
docker exec portal-django /bin/bash -c "source .env; source .venv/bin/activate; ./dumpdata.sh"
```

Example output:

```console
$ docker exec portal-django /bin/bash -c "source .env; source .venv/bin/activate; ./dumpdata.sh"
python3 ./manage.py dumpdata credentials --indent 2 --output ./dumpdata/credentials.json
python3 ./manage.py dumpdata experiment_files --indent 2 --output ./dumpdata/experiment_files.json
python3 ./manage.py dumpdata experiments --indent 2 --output ./dumpdata/experiments.json
python3 ./manage.py dumpdata operations --indent 2 --output ./dumpdata/operations.json
python3 ./manage.py dumpdata profiles --indent 2 --output ./dumpdata/profiles.json
python3 ./manage.py dumpdata projects --indent 2 --output ./dumpdata/projects.json
python3 ./manage.py dumpdata resources --indent 2 --output ./dumpdata/resources.json
python3 ./manage.py dumpdata user_messages --indent 2 --output ./dumpdata/user_messages.json
python3 ./manage.py dumpdata user_requests --indent 2 --output ./dumpdata/user_requests.json
python3 ./manage.py dumpdata users --indent 2 --output ./dumpdata/users.json
```

### The JSON fixture files

Once completed the JSON data will be found in the dumpdata directory

```console
$ ls -lh dumpdata
total 304
-rw-r--r--  1 username  staff    13K Nov 17 17:50 credentials.json
-rw-r--r--  1 username  staff    33K Nov 17 17:50 experiment_files.json
-rw-r--r--  1 username  staff    55K Nov 17 17:50 experiments.json
-rw-r--r--  1 username  staff   4.4K Nov 17 17:50 operations.json
-rw-r--r--  1 username  staff   4.1K Nov 17 17:50 profiles.json
-rw-r--r--  1 username  staff   5.6K Nov 17 17:50 projects.json
-rw-r--r--  1 username  staff   2.9K Nov 17 17:50 resources.json
-rw-r--r--  1 username  staff     4B Nov 17 17:50 user_messages.json
-rw-r--r--  1 username  staff   1.2K Nov 17 17:50 user_requests.json
-rw-r--r--  1 username  staff   5.4K Nov 17 17:50 users.json
```

**Note**: when running in docker it is possible that the data will be owned by the `root` user due to how Docker works. The user will want to change file ownership to be the same as the user that ran the containers initially.

## Restoring the database from JSON fixtures

The fixture files (when present) are loaded at runtime with the load fixtures flag is set

Fixtures will be loaded form the `portal/apps/users/fixtures` directory, and any fixtures that the user wants loaded should be copies there prior to starting the service

Initially there is only the `aerpaw_roles.json` file

```console
$ ls -lh portal/apps/users/fixtures
total 304
-rw-r--r--  1 username  staff   487B Oct 27 10:39 aerpaw_roles.json
```

But the user can copy the files from the dumpdata directory to the fixtures directory to be used on the subsequent run

```console
cp dumpdata/*.json portal/apps/users/fixtures
```

```console
$ ls -lh portal/apps/users/fixtures
total 312
-rw-r--r--  1 username  staff   487B Oct 27 10:39 aerpaw_roles.json
-rw-r--r--  1 username  staff    13K Nov 17 18:07 credentials.json
-rw-r--r--  1 username  staff    33K Nov 17 18:07 experiment_files.json
-rw-r--r--  1 username  staff    55K Nov 17 18:07 experiments.json
-rw-r--r--  1 username  staff   4.4K Nov 17 18:07 operations.json
-rw-r--r--  1 username  staff   4.1K Nov 17 18:07 profiles.json
-rw-r--r--  1 username  staff   5.6K Nov 17 18:07 projects.json
-rw-r--r--  1 username  staff   2.9K Nov 17 18:07 resources.json
-rw-r--r--  1 username  staff     4B Nov 17 18:07 user_messages.json
-rw-r--r--  1 username  staff   1.2K Nov 17 18:07 user_requests.json
-rw-r--r--  1 username  staff   5.4K Nov 17 18:07 users.json
```

### Local Development

Fixtures are then loaded when flag is present at runtime

```console
--load-fixtures
```

### In Docker

Fixtures are then loaded when variable is present at runtime

```console
LOAD_FIXTURES=1
```


Back to [README](../README.md)

#!/usr/bin/env bash

PARAMS=""
while (("$#")); do
    case "$1" in
    -l | --load-fixtures)
        LOAD_FIXTURES=1
        shift
        ;;
    -m | --mode)
        if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
            MODE=$2
            shift 2
            case "$MODE" in
                local-dev | local-ssl | docker)
                    ;;
                *)
                    echo "InvalidMode: -m | --mode <local-dev | local-ssl | docker>"
                    exit 1
                    ;;
            esac
        else
            echo "Error: Argument for $1 is missing" >&2
            exit 1
        fi
        ;;
    -* | --*=) # unsupported flags
        echo "Error: Unsupported flag $1" >&2
        exit 1
        ;;
    *) # preserve positional arguments
        PARAMS="$PARAMS $1"
        shift
        ;;
    esac
done
# set positional arguments in their proper place
eval set -- "$PARAMS"

# load fixtures
if [[ "${LOAD_FIXTURES}" -eq 1 ]]; then
    echo "### LOAD_FIXTURES = True ###"
    APPS_LIST=(
        "mixins"
        "users"
        "profiles"
        "resources"
        "projects"
        "experiment_files"
        "experiments"
        "operations"
        "credentials"
    )

    FIXTURES_LIST=(
        "aerpaw_roles"
        "resources"
        "operations"
        "profiles"
        "users"
        "credentials"
        "projects"
        "experiment_files"
        "experiments"
        "user_messages"
        "user_requests"
    )
else
    echo "### LOAD_FIXTURES = False ###"
    APPS_LIST=()
    FIXTURES_LIST=()
fi

# migrations files
for app in "${APPS_LIST[@]}"; do
    python manage.py makemigrations $app
done
python manage.py makemigrations
python manage.py showmigrations
python manage.py migrate

# load fixtures
for fixture in "${FIXTURES_LIST[@]}"; do
    python manage.py loaddata $fixture
done

# static files
python manage.py collectstatic --noinput

# run mode
case "${MODE}" in
    local-dev)
        echo "local-dev"
        python manage.py runserver 0.0.0.0:8000
        ;;
    local-ssl)
        echo "local-ssl"
        uwsgi --uid ${UWSGI_UID:-1000} --gid ${UWSGI_GID:-1000} --virtualenv ./venv --ini aerpaw-portal.ini
        ;;
    docker)
        echo "docker"
        uwsgi --uid ${UWSGI_UID:-1000} --gid ${UWSGI_GID:-1000} --virtualenv ./.venv --ini aerpaw-portal.ini
        ;;
    *)
        echo "ModeRequired: -m | --mode <local-dev | local-ssl | docker>"
        exit 1
        ;;
esac

exit 0
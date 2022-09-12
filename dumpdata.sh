#!/usr/bin/env bash

APPS_LIST=(
    "credentials"
    "experiment_files"
    "experiments"
    "operations"
    "profiles"
    "projects"
    "resources"
    "user_messages"
    "user_requests"
    "users"
)

for app in "${APPS_LIST[@]}";do
    echo "python3 ./manage.py dumpdata ${app} --indent 2 --output ./dumpdata/${app}.json"
    python3 ./manage.py dumpdata "${app}" --indent 2 --output ./dumpdata/"${app}".json
done

exit 0;

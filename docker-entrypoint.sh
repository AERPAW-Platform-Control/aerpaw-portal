#!/usr/bin/env bash
set -e

source .env
virtualenv -p /usr/local/bin/python .venv
source .venv/bin/activate
pip install -r requirements.txt

#chown -R ${UWSGI_UID:-1000}:${UWSGI_GID:-1000} .venv

until [ "$(pg_isready -h database -q)"$? -eq 0 ]; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing"

if [[ "${LOAD_FIXTURES}" -eq 1 ]]; then
    ./run_server.sh --mode docker --load-fixtures
else
    ./run_server.sh --mode docker
fi

exec "$@"

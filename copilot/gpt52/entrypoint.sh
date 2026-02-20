#!/usr/bin/env sh
set -eu

mkdir -p /app/data

python manage.py migrate --noinput

exec "$@"

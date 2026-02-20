#!/usr/bin/env bash
set -e

mkdir -p /app/db_data

# Mantém o SQLite em um caminho persistente no volume, mas sem quebrar o settings padrão.
# Criamos um symlink db.sqlite3 -> db_data/db.sqlite3
if [ ! -L /app/db.sqlite3 ]; then
  if [ -f /app/db.sqlite3 ]; then
    rm -f /app/db.sqlite3
  fi
  ln -s /app/db_data/db.sqlite3 /app/db.sqlite3
fi

python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000

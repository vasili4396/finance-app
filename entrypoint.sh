#!/bin/bash

set -e
set -o pipefail

if [[ $1 == "runserver" ]]; then
  python manage.py migrate
  python manage.py ensure_superuser
  python manage.py runserver 0.0.0.0:8000
fi

if [[ $1 == "fill_db" ]]; then
  python manage.py migrate
  python manage.py fill_db
fi

if [[ $1 == "test" ]]; then
  python test_project/manage.py test --noinput --verbosity 2
fi

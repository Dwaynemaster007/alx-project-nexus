#!/usr/bin/env bash
# Render build command: ./build.sh   (root directory: backend)
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input

#! /usr/bin/env sh
set -e

DEFAULT_GUNICORN_CONF=/data/python/gunicorn.py
export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}

# Start Gunicorn
exec gunicorn -c "$GUNICORN_CONF" main:app
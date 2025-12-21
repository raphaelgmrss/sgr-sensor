#!/usr/bin/env bash
set -e

gunicorn \
  --chdir /app/api \
  --bind 0.0.0.0:5000 \
  run:app &

exec nginx -g "daemon off;"

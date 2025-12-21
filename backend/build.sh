#!/usr/bin/env bash
set -e

python3 -m compileall ./api -b

mkdir -p ./dist/api

rsync -av \
  --include="*/" \
  --include="*.pyc" \
  --exclude="*" \
  ./api/ ./dist/api/

cp -r ./database ./dist

find ./dist/api -name "*.py" -delete

find ./dist/api -type d \( \
  -name "__pycache__" -o \
  -name "instance" -o \
  -name "migrations" \
\) -prune -exec rm -rf {} +


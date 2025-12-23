#!/usr/bin/env bash
set -e

pyarmor gen \
  --recursive \
  --output dist \
  ../api/

python3 -m compileall ./dist/api -b

cp -r ../database ./dist

find ./dist/api -name "*.py" -delete

find ./dist/api -type d \( \
  -name "__pycache__" -o \
  -name "instance" -o \
  -name "migrations" \
\) -prune -exec rm -rf {} +

mv ./dist/pyarmor_runtime_000000 ./dist/api/
cp -r ../database ./dist
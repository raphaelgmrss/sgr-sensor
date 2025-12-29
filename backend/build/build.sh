#!/usr/bin/env bash
set -e

rm -rf dist

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

cd ../../

docker stop sgr-sensor && docker rm sgr-sensor && docker rmi sgr-sensor
docker build -t sgr-sensor .
docker run -d --name sgr-sensor -p 8080:80 -e API_URL=http://localhost:8080/api sgr-sensor
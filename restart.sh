#!/usr/bin/env bash

docker-compose down
docker rmi `docker images -a -q`
docker rmi pawprints_huey_worker:latest
docker rmi pawprints_worker:latest

pip freeze > requirements.txt
docker-compose up --build

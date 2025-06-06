#!/bin/bash

set -e
docker-compose up -d
echo "App is running"
docker exec -it book-tracker-fastapi bash -c "alembic upgrade head"
echo "Added migrations"

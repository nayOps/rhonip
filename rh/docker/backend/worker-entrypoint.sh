#!/bin/sh

until cd /app/backend
do
    echo "Waiting for server volume..."
done

celery -A payday worker -l info -c 4 --beat -E

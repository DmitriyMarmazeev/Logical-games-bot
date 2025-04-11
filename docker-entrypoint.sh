#!/bin/bash

mkdir -p /app/data

if [ ! -f "/app/data/database.db" ]; then
    cp /app/database.db /app/data/
    echo "Инициализирована новая база данных"
else
    echo "Используется существующая база данных"
fi

exec "$@"